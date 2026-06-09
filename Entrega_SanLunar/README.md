# San Lunar: Cristais da Maré

Demo de jogo 2D em Python criada para a atividade. O jogo usa `pygame`, abre em uma janela propria e nao roda via console/CMD.

## Tema

Voce controla um explorador lunar em uma missao de resgate. O objetivo e coletar 6 cristais lunares, desviar dos meteoros e voltar para o modulo antes que o oxigenio acabe.

## Controles

- Setas ou WASD: mover
- Space: propulsor rapido
- Enter: iniciar no menu
- R: reiniciar depois de vencer/perder
- Esc: voltar ao menu

## Condicoes da demo

- Controle do jogador: movimento livre em 2D.
- Desafio: meteoros caem pela tela e causam dano.
- Vitoria: coletar 6 cristais e entrar no modulo lunar.
- Derrota: perder toda a vida ou ficar sem oxigenio.
- Menu: possui nome, objetivo e comandos de controle.

## Rodar pelo Python

```bat
python -m pip install pygame
python main.py
```

Caso sua maquina use o launcher do Windows:

```bat
py -m pip install pygame
py main.py
```

## Gerar o EXE no Windows

1. Instale o PyInstaller, se necessario:

```bat
python -m pip install pyinstaller
```

2. Execute:

```bat
build_windows.bat
```

O executavel sera gerado em:

```text
dist\SanLunar.exe
```

Para entregar, compacte a pasta `dist` junto com este README e a pasta `assets`, mantendo a hierarquia de pastas.

## Observacao sobre caminhos relativos

O projeto usa caminhos relativos baseados na pasta do script (`main.py`). Nao ha caminhos absolutos dentro do codigo do jogo.
