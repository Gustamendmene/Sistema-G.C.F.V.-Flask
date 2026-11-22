from banco.conexao import conectar


def _consultar(sql):
    """Executa um SELECT e devolve todas as linhas."""
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(sql)
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def listar_alertas():
    """Produtos vencidos, perto de vencer (7 dias) ou com estoque baixo."""
    return _consultar("SELECT * FROM alerta_estoque")


def listar_alertas_validade():
    """Produtos vencidos ou que vencem nos próximos 7 dias."""
    return _consultar("""
        SELECT p.id_produto, p.nome, p.data_validade,
               DATEDIFF(p.data_validade, CURDATE()) AS dias,
               e.quantidade_atual
        FROM produto p
        JOIN estoque e ON e.id_produto = p.id_produto
        WHERE p.data_validade < CURDATE()
           OR DATEDIFF(p.data_validade, CURDATE()) <= 7
        ORDER BY p.data_validade, p.nome
    """)


def contar_alertas():
    return len(listar_alertas())


def resumo_estoque():
    """Devolve (produtos, próximos do vencimento, vencidos)."""
    linhas = _consultar("""
        SELECT
            (SELECT COUNT(*) FROM produto),
            (SELECT COUNT(*) FROM produto
              WHERE data_validade >= CURDATE()
                AND DATEDIFF(data_validade, CURDATE()) <= 7),
            (SELECT COUNT(*) FROM produto WHERE data_validade < CURDATE())
    """)
    return linhas[0]


def listar_estoque():
    """Devolve (produto, quantidade atual, quantidade mínima, atualizado em)."""
    return _consultar("""
        SELECT p.nome, e.quantidade_atual, e.quantidade_minima,
               e.data_atualizacao
        FROM estoque e
        JOIN produto p ON p.id_produto = e.id_produto
        ORDER BY p.nome
    """)
