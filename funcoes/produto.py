from banco.conexao import conectar
from funcoes.models.productDTO import ProductDTO


def inserir_produto(nome, categoria, marca, codigo_barras, fornecedor,
                    preco_custo, preco_venda, data_entrega, data_validade,
                    quantidade, quantidade_minima, lote, localizacao):
    """Cadastra o produto e já cria a linha dele no estoque."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """INSERT INTO produto (nome, categoria, marca, codigo_barras,
               fornecedor, preco_custo, preco_venda, data_entrega,
               data_validade)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (nome, categoria, marca, codigo_barras, fornecedor,
             preco_custo, preco_venda, data_entrega, data_validade),
        )
        id_produto = cur.lastrowid
        cur.execute(
            """INSERT INTO estoque (id_produto, quantidade_atual,
               quantidade_minima, lote, localizacao)
               VALUES (%s,%s,%s,%s,%s)""",
            (id_produto, quantidade, quantidade_minima, lote, localizacao),
        )
        con.commit()
        return id_produto
    except Exception:
        con.rollback()  
        raise
    finally:
        cur.close()
        con.close()


def deletar_produto(id_produto):
    """Apaga o produto; o estoque dele some junto (ON DELETE CASCADE)."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
        con.commit()
        return cur.rowcount  
    finally:
        cur.close()
        con.close()
        
def update_produto(id_produto, product_dto: ProductDTO):
    """Atualiza os dados do produto e do estoque."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """UPDATE produto
               SET nome=%s, categoria=%s, marca=%s, codigo_barras=%s,
                   fornecedor=%s, preco_custo=%s, preco_venda=%s,
                   data_entrega=%s, data_validade=%s
               WHERE id_produto=%s""",
            (product_dto.nome, product_dto.categoria, product_dto.marca, product_dto.codigo_barras, product_dto.fornecedor,
             product_dto.preco_custo, product_dto.preco_venda, product_dto.data_entrega, product_dto.data_validade,
             id_produto),
        )
        cur.execute(
            """UPDATE estoque
               SET quantidade_atual=%s, quantidade_minima=%s,
                   lote=%s, localizacao=%s
               WHERE id_produto=%s""",
            (product_dto.quantidade, product_dto.quantidade_minima, product_dto.lote, product_dto.localizacao,
             id_produto),
        )
        con.commit()
        return cur.rowcount  
    except Exception:
        con.rollback()  
        raise
    finally:
        cur.close()
        con.close()

def listar_produtos():
    """Devolve os dados exibidos na tabela e usados para editar cada produto."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """SELECT p.id_produto, p.nome, p.categoria, p.data_validade,
                      e.quantidade_atual, e.localizacao, p.marca,
                      p.codigo_barras, p.fornecedor, p.preco_custo,
                      p.preco_venda, p.data_entrega, e.quantidade_minima,
                      e.lote
               FROM produto p
               JOIN estoque e ON e.id_produto = p.id_produto
               ORDER BY p.nome"""
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def obter_produto(id_produto):
    """Busca os campos editáveis do produto e do estoque."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            """SELECT p.nome, p.categoria, p.marca, p.codigo_barras,
                      p.fornecedor, p.preco_custo, p.preco_venda,
                      p.data_entrega, p.data_validade, e.quantidade_atual,
                      e.quantidade_minima, e.lote, e.localizacao
               FROM produto p JOIN estoque e ON e.id_produto = p.id_produto
               WHERE p.id_produto = %s""",
            (id_produto,),
        )
        linha = cur.fetchone()
        if linha is None:
            return None
        chaves = ("nome", "categoria", "marca", "codigo_barras", "fornecedor",
                  "preco_custo", "preco_venda", "data_entrega", "data_validade",
                  "quantidade", "quantidade_minima", "lote", "localizacao")
        return dict(zip(chaves, linha))
    finally:
        cur.close()
        con.close()
