import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()  

from funcoes.models.productDTO import ProductDTO
from funcoes.produto import inserir_produto, deletar_produto, listar_produtos, update_produto, obter_produto
from funcoes.estoque import (
    resumo_estoque,
    listar_alertas,
    listar_lotes,
    listar_estoque,
)
from icones import icone

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mercadinho-sao-jose")
app.add_template_global(icone, "icone")

CORES_ALERTA = {
    "VENCIDO": "vermelho",
    "PRÓXIMO DO VENCIMENTO": "amarelo",
    "ESTOQUE BAIXO": "laranja",
}


def formatar_data(valor):
    """Mostra datas vindas do banco no formato dd/mm/aaaa."""
    if valor is None:
        return "-"
    try:
        return valor.strftime("%d/%m/%Y")
    except AttributeError:
        return str(valor)


app.add_template_filter(formatar_data, "data_br")


def etiqueta(texto, cor):
    """Célula de tabela exibida como uma 'etiqueta' colorida."""
    return {"texto": texto, "cor": cor}


def linhas_lotes():
    return [
        (lote or "-", nome, formatar_data(validade), qtd, local or "-")
        for lote, nome, validade, qtd, local in listar_lotes()
    ]


def linhas_estoque():
    linhas = []
    for nome, qtd, minimo, atualizado in listar_estoque():
        if qtd <= minimo:
            situacao = etiqueta("ESTOQUE BAIXO", "laranja")
        else:
            situacao = etiqueta("OK", "verde")
        linhas.append((nome, qtd, minimo, situacao, formatar_data(atualizado)))
    return linhas


def linhas_validade():
    alertas = sorted(listar_alertas(), key=lambda linha: linha[3])
    linhas = []
    for id_p, nome, validade, dias, qtd, minimo, alerta in alertas:
        if dias < 0:
            prazo = f"venceu há {-dias} dia(s)"
        elif dias == 0:
            prazo = "vence hoje"
        else:
            prazo = f"{dias} dia(s)"
        linhas.append((
            id_p, nome, formatar_data(validade), prazo, qtd, minimo,
            etiqueta(alerta or "-", CORES_ALERTA.get(alerta, "azul")),
        ))
    return linhas


def pagina_tabela(pagina, titulo, subtitulo, colunas, buscar, vazio):
    """Monta uma tela de consulta (Lotes, Estoque e Validade)."""
    erro, linhas = None, []
    try:
        linhas = buscar()
    except Exception as e:
        erro = f"Não foi possível ler o banco de dados: {e}"
    return render_template(
        "tabela.html", pagina=pagina, titulo=titulo, subtitulo=subtitulo,
        colunas=colunas, linhas=linhas, erro=erro, vazio=vazio,
    )


def pagina_produtos(form=None, erro_form=None):
    """Tela de produtos. Se o cadastro deu erro, devolve o que foi digitado."""
    lista, erro_banco = [], None
    try:
        lista = listar_produtos()
    except Exception as e:
        erro_banco = f"Não foi possível ler os produtos do banco: {e}"
    return render_template(
        "produtos.html", pagina="produtos", produtos=lista,
        form=form or {}, erro_form=erro_form, erro_banco=erro_banco,
    )




@app.route("/")
def inicio():
    erro = None
    try:
        total_produtos, total_lotes, proximos, vencidos = resumo_estoque()
    except Exception as e:
        total_produtos = total_lotes = proximos = vencidos = 0
        erro = ("Não foi possível ler o banco de dados. Confira se o MySQL "
                f"está ligado e se o .env está correto. ({e})")
    return render_template(
        "inicio.html", pagina="inicio", erro=erro,
        total_produtos=total_produtos, total_lotes=total_lotes,
        proximos=proximos, vencidos=vencidos,
    )


@app.route("/produtos")
def produtos():
    return pagina_produtos()


@app.route("/produtos/salvar", methods=["POST"])
def salvar_produto():
    f = {chave: valor.strip() for chave, valor in request.form.items()}
    try:
        preco_venda = float(f.get("preco_venda", "").replace(",", "."))
        preco_custo = (float(f["preco_custo"].replace(",", "."))
                       if f.get("preco_custo") else 0)
        entrega = datetime.strptime(f.get("data_entrega", ""), "%Y-%m-%d").date()
        validade = datetime.strptime(f.get("data_validade", ""), "%Y-%m-%d").date()
        quantidade = int(f.get("quantidade", ""))
        minima = (int(f["quantidade_minima"])
                  if f.get("quantidade_minima") else 5)
    except ValueError:
        return pagina_produtos(
            f, "Confira os campos com *: preço de venda (ex.: 25,90), "
               "datas completas e quantidade em números inteiros.")

    if not f.get("nome"):
        return pagina_produtos(f, "Informe o nome do produto.")
    if validade < entrega:
        return pagina_produtos(
            f, "A validade não pode ser anterior à data de entrega.")
    if quantidade < 0 or minima < 0:
        return pagina_produtos(f, "As quantidades não podem ser negativas.")

    try:
        inserir_produto(
            f["nome"], f.get("categoria", ""), f.get("marca", ""),
            f.get("codigo_barras") or None,  
            f.get("fornecedor", ""), preco_custo, preco_venda,
            entrega, validade, quantidade, minima,
            f.get("lote", ""), f.get("localizacao", ""),
        )
    except Exception as e:
        return pagina_produtos(f, f"Não foi possível salvar o produto: {e}")

    flash(f"Produto '{f['nome']}' salvo com sucesso.", "ok")
    return redirect(url_for("produtos"))

@app.route("/produtos/<int:id_produto>/editar", methods=["POST"])
def atualizar_produto(id_produto):
    atual = obter_produto(id_produto)
    if atual is None:
        flash("Esse produto não existe mais.", "erro")
        return redirect(url_for("produtos"))

    def valor_form(valor):
        if valor is None:
            return ""
        return valor.isoformat() if hasattr(valor, "isoformat") else str(valor)

    f = {chave: valor_form(valor) for chave, valor in atual.items()}
    f.update({chave: valor.strip() for chave, valor in request.form.items()})
    modificados = [chave for chave, antigo in atual.items()
                   if f.get(chave, "") != valor_form(antigo)]
    if not modificados:
        flash("Edite pelo menos um campo antes de salvar.", "erro")
        return redirect(url_for("produtos"))

    # Campos numéricos ou datas vazios mantêm o valor atual.
    for chave in ("preco_custo", "preco_venda", "data_entrega", "data_validade",
                  "quantidade", "quantidade_minima"):
        if not f.get(chave):
            f[chave] = valor_form(atual[chave])
    try:
        preco_venda = float(f.get("preco_venda", "").replace(",", "."))
        preco_custo = (float(f["preco_custo"].replace(",", "."))
                       if f.get("preco_custo") else 0)
        entrega = datetime.strptime(f.get("data_entrega", ""), "%Y-%m-%d").date()
        validade = datetime.strptime(f.get("data_validade", ""), "%Y-%m-%d").date()
        quantidade = int(f.get("quantidade", ""))
        minima = (int(f["quantidade_minima"])
                  if f.get("quantidade_minima") else 5)
    except ValueError:
        return pagina_produtos(
            f, "Confira os campos com *: preço de venda (ex.: 25,90), "
               "datas completas e quantidade em números inteiros.")

    if not f.get("nome"):
        return pagina_produtos(f, "Informe o nome do produto.")
    if validade < entrega:
        return pagina_produtos(
            f, "A validade não pode ser anterior à data de entrega.")
    if quantidade < 0 or minima < 0:
        return pagina_produtos(f, "As quantidades não podem ser negativas.")

    product_dto = ProductDTO(
        nome=f["nome"],
        categoria=f.get("categoria", ""),
        marca=f.get("marca", ""),
        codigo_barras=f.get("codigo_barras") or None,
        fornecedor=f.get("fornecedor", ""),
        preco_custo=preco_custo,
        preco_venda=preco_venda,
        data_entrega=entrega,
        data_validade=validade,
        quantidade=quantidade,
        quantidade_minima=minima,
        lote=f.get("lote", ""),
        localizacao=f.get("localizacao", "")
    )

    try:
        update_produto(id_produto, product_dto)
        flash(f"Produto '{f['nome']}' atualizado com sucesso.", "ok")
        return redirect(url_for("produtos"))
    except Exception as e:
        return pagina_produtos(f, f"Não foi possível atualizar o produto: {e}")


@app.route("/produtos/<int:id_produto>/excluir", methods=["POST"])
def excluir_produto(id_produto):
    try:
        removidos = deletar_produto(id_produto)
    except Exception as e:
        flash(f"Não foi possível excluir o produto: {e}", "erro")
        return redirect(url_for("produtos"))
    if removidos:
        flash("Produto excluído.", "ok")
    else:
        flash("Esse produto já não existe.", "erro")
    return redirect(url_for("produtos"))


@app.route("/lotes")
def lotes():
    return pagina_tabela(
        "lotes", "Lotes", "Lotes registrados, com validade e quantidade.",
        ["Lote", "Produto", "Validade", "Quantidade", "Local"],
        linhas_lotes,
        "Nenhum lote registrado ainda. Cadastre um produto na tela Produtos.",
    )


@app.route("/estoque")
def estoque():
    return pagina_tabela(
        "estoque", "Estoque",
        "Quantidade atual de cada produto e o mínimo desejado.",
        ["Produto", "Quantidade", "Mínimo", "Situação", "Atualizado em"],
        linhas_estoque,
        "O estoque está vazio. Cadastre um produto na tela Produtos.",
    )


@app.route("/validade")
def validade():
    return pagina_tabela(
        "validade", "Controle de validade",
        "Produtos vencidos, que vencem em até 7 dias ou com estoque baixo.",
        ["ID", "Produto", "Validade", "Prazo", "Quantidade", "Mínimo",
         "Alerta"],
        linhas_validade,
        "Nenhum alerta no momento. Tudo dentro da validade e do estoque "
        "mínimo.",
    )


if __name__ == "__main__":
    app.run(debug=True)
