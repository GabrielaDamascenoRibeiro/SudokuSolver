
import streamlit as st
import numpy as np
import math
from ortools.sat.python import cp_model

st.set_page_config(page_title="Sudoku Solver com OR-Tools", layout="centered")

st.title("🧠 Resolvedor de Sudoku com OR-Tools")
st.markdown("Escolha o tamanho da grade, preencha os números conhecidos e clique em **Resolver**.")

# 1. Tamanho da grade
n = st.selectbox("Tamanho do Sudoku", [4, 9, 16], index=2)
block_size = int(math.sqrt(n))

# 2. Inserção dos dados
st.markdown("### Insira os números conhecidos (deixe em branco para vazio):")

sudoku_input = []
cols = st.columns(n)
for i in range(n):
    row = []
    for j in range(n):
        with cols[j]:
            cell = st.text_input(f"{i+1},{j+1}", "", key=f"cell-{i}-{j}")
            row.append(int(cell) if cell.strip().isdigit() else 0)
    sudoku_input.append(row)

sudoku = np.array(sudoku_input)

# 3. Função para resolver com OR-Tools
def solve_sudoku_cp(sudoku, n):
    model = cp_model.CpModel()
    block_size = int(math.sqrt(n))

    # Criação das variáveis
    cells = [[model.NewIntVar(1, n, f'cell_{r}_{c}') for c in range(n)] for r in range(n)]

    # Restrições fixas (entradas conhecidas)
    for r in range(n):
        for c in range(n):
            if sudoku[r][c] != 0:
                model.Add(cells[r][c] == sudoku[r][c])

    # Linhas e colunas
    for i in range(n):
        model.AddAllDifferent([cells[i][j] for j in range(n)])
        model.AddAllDifferent([cells[j][i] for j in range(n)])

    # Blocos
    for box_row in range(0, n, block_size):
        for box_col in range(0, n, block_size):
            box = [cells[r][c]
                   for r in range(box_row, box_row + block_size)
                   for c in range(box_col, box_col + block_size)]
            model.AddAllDifferent(box)

    # Resolver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return [[solver.Value(cells[r][c]) for c in range(n)] for r in range(n)]
    else:
        return None

# 4. Botão de resolução
if st.button("✅ Resolver"):
    with st.spinner("Resolvendo..."):
        solution = solve_sudoku_cp(sudoku, n)

    if solution:
        st.success("Sudoku resolvido com sucesso!")
        st.markdown("### Solução:")

        for i in range(n):
            cols_res = st.columns(n)
            for j in range(n):
                with cols_res[j]:
                    st.text_input(f"{i+1},{j+1}-res", str(solution[i][j]), key=f"res-{i}-{j}", disabled=True)
    else:
        st.error("Não foi possível encontrar uma solução.")
