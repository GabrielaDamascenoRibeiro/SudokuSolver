import streamlit as st
import numpy as np
import math
from ortools.sat.python import cp_model

st.set_page_config(page_title="Sudoku Solver", layout="wide")

st.title("🧠 Resolvedor de Sudoku")
st.markdown(
    """
    Escolha o tamanho da grade, insira os números conhecidos abaixo (uma linha para cada linha da grade, números separados por espaço ou vírgula). 
    Use 0 para células vazias.
    """
)

# 1. Seleção do tamanho do sudoku
n = st.selectbox("Tamanho do Sudoku", [4, 9, 16], index=2)
block_size = int(math.sqrt(n))

# 2. Entrada multilinha da grade
default_text = "\n".join([" ".join(["0"]*n) for _ in range(n)])
input_text = st.text_area("Insira a grade do Sudoku:", default_text, height=300)

# Função para processar entrada do usuário em matriz numpy
def parse_input(text, n):
    lines = text.strip().split("\n")
    board = []
    for line in lines:
        # Limpar linha e separar por espaço ou vírgula
        line_clean = line.replace(",", " ").strip()
        row_vals = line_clean.split()
        if len(row_vals) != n:
            raise ValueError(f"Cada linha deve conter exatamente {n} números.")
        row_ints = [int(x) if x.isdigit() else 0 for x in row_vals]
        board.append(row_ints)
    if len(board) != n:
        raise ValueError(f"O número de linhas deve ser exatamente {n}.")
    return np.array(board)

def solve_sudoku_cp(sudoku, n):
    model = cp_model.CpModel()
    block_size = int(math.sqrt(n))
    cells = [[model.NewIntVar(1, n, f'cell_{r}_{c}') for c in range(n)] for r in range(n)]

    for r in range(n):
        for c in range(n):
            if sudoku[r][c] != 0:
                model.Add(cells[r][c] == sudoku[r][c])

    for i in range(n):
        model.AddAllDifferent([cells[i][j] for j in range(n)])
        model.AddAllDifferent([cells[j][i] for j in range(n)])

    for box_row in range(0, n, block_size):
        for box_col in range(0, n, block_size):
            block = [cells[r][c]
                     for r in range(box_row, box_row + block_size)
                     for c in range(box_col, box_col + block_size)]
            model.AddAllDifferent(block)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return [[solver.Value(cells[r][c]) for c in range(n)] for r in range(n)]
    else:
        return None

if st.button("✅ Resolver"):
    try:
        sudoku = parse_input(input_text, n)
    except Exception as e:
        st.error(f"Erro ao processar entrada: {e}")
    else:
        with st.spinner("Resolvendo..."):
            solution = solve_sudoku_cp(sudoku, n)
        if solution:
            st.success("Sudoku resolvido com sucesso!")
            st.markdown("### Solução:")
            # Mostrar solução com scroll horizontal
            st.dataframe(np.array(solution), width=1000, height=400)
        else:
            st.error("Não foi possível encontrar uma solução.")
