class ProductDTO:
    def __init__(self, nome, categoria, marca, codigo_barras, fornecedor,
                 preco_custo, preco_venda, data_entrega, data_validade,
                 quantidade, quantidade_minima, lote, localizacao):
        self.nome = nome
        self.categoria = categoria  
        self.marca = marca
        self.codigo_barras = codigo_barras
        self.fornecedor = fornecedor
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.data_entrega = data_entrega
        self.data_validade = data_validade
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima
        self.lote = lote
        self.localizacao = localizacao