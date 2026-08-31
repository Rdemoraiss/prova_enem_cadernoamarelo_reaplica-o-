from PIL import Image
import os

def encontrar_faixa_cinza(imagem, cor_alvo=(189, 188, 188), tolerancia_cor=15, altura_alvo=64, margem_altura=4):
    """
    Encontra posições onde há uma faixa vertical/horizontal da cor especificada
    na coluna do antepenúltimo pixel da direita (largura - 3).
    A aceitação de altura considera a margem de erro (60 a 68 pixels).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Limites para aceitação da altura da faixa (64 ± 4 pixels)
    altura_minima = altura_alvo - margem_altura  # 60 pixels
    altura_maxima = altura_alvo + margem_altura  # 68 pixels
    
    # Percorre a imagem de cima para baixo no antepenúltimo pixel da direita
    x_coluna = largura - 3
    y = 0
    
    while y < altura:
        # Pega a cor do pixel atual
        pixel = pixels[x_coluna, y]
        r, g, b = pixel[:3]
        
        # Verifica se o pixel inicial bate com a cor alvo dentro da tolerância
        if (abs(r - cor_alvo[0]) <= tolerancia_cor and 
            abs(g - cor_alvo[1]) <= tolerancia_cor and 
            abs(b - cor_alvo[2]) <= tolerancia_cor):
            
            # Conta quantos pixels consecutivos abaixo têm a mesma cor
            altura_contada = 0
            while (y + altura_contada) < altura:
                p_atual = pixels[x_coluna, y + altura_contada][:3]
                if (abs(p_atual[0] - cor_alvo[0]) <= tolerancia_cor and 
                    abs(p_atual[1] - cor_alvo[1]) <= tolerancia_cor and 
                    abs(p_atual[2] - cor_alvo[2]) <= tolerancia_cor):
                    altura_contada += 1
                else:
                    break
            
            # Avalia se a faixa contada está dentro da margem de erro (60 a 68 px)
            if altura_minima <= altura_contada <= altura_maxima:
                posicao_corte = y
                posicoes_corte.append(posicao_corte)
                print(f"Padrão encontrado em y={y} (altura de {altura_contada}px), cortando em y={posicao_corte}")
                
                # Avança a varredura pulando a faixa encontrada
                y += altura_contada
                continue
            else:
                # Se a faixa não tinha a altura desejada, avança o bloco contado para não reavaliar
                y += max(1, altura_contada)
                continue
        
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando no início das faixas encontradas.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições dos padrões cinza
    posicoes_corte = encontrar_faixa_cinza(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final (após o último corte até o fim da imagem)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "./inteiras/pagina_enem_19.png"  # Atualize para o nome da sua imagem
    pasta_saida = "pg19"                      # Atualize para o nome da pasta de saída
    
    # Cor direta em RGB (0-255)
    cor_do_padrao = (189, 188, 188)
    print(f"Buscando padrão na cor RGB: {cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")