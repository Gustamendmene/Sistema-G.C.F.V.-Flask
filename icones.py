from markupsafe import Markup

_CAMINHOS = {
    "inicio": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
              '<polyline points="9 22 9 12 15 12 15 22"/>',
    "produtos": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
                '<polyline points="3.27 6.96 12 12.01 20.73 6.96"/>'
                '<line x1="12" y1="22.08" x2="12" y2="12"/>',
    "estoque": '<polyline points="21 8 21 21 3 21 3 8"/>'
               '<rect x="1" y="3" width="22" height="5"/>'
               '<line x1="10" y1="12" x2="14" y2="12"/>',
    "validade": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
                '<line x1="16" y1="2" x2="16" y2="6"/>'
                '<line x1="8" y1="2" x2="8" y2="6"/>'
                '<line x1="3" y1="10" x2="21" y2="10"/>',
    "sino": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>'
            '<path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "lixeira": '<polyline points="3 6 5 6 21 6"/>'
               '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
               '<path d="M10 11v6"/><path d="M14 11v6"/>'
               '<path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>',
    "relogio": '<circle cx="12" cy="12" r="10"/>'
               '<polyline points="12 6 12 12 16 14"/>',
    "alerta": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
              '<line x1="12" y1="9" x2="12" y2="13"/>'
              '<line x1="12" y1="17" x2="12.01" y2="17"/>',
    "seta": '<line x1="5" y1="12" x2="19" y2="12"/>'
            '<polyline points="12 5 19 12 12 19"/>',
    "mais": '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>'
            '<line x1="12" y1="8" x2="12" y2="16"/>'
            '<line x1="8" y1="12" x2="16" y2="12"/>',
}


def icone(nome, tamanho=22):
    """Devolve o ícone pronto para colocar no HTML: {{ icone('inicio') }}"""
    caminho = _CAMINHOS.get(nome, "")
    return Markup(
        f'<svg class="icone" width="{tamanho}" height="{tamanho}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{caminho}</svg>'
    )