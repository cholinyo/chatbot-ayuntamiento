import faiss
import pickle
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Cargar índice y metadatos
index = faiss.read_index("faiss_data/faiss.index")
with open("faiss_data/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

vectores = [index.reconstruct(i) for i in range(len(metadata))]
etiquetas = [m["texto"][:60].replace("\n", " ") for m in metadata]

# Escalar y reducir a 2D
vectores_escalados = StandardScaler().fit_transform(vectores)
vectores_2d = PCA(n_components=2).fit_transform(vectores_escalados)

# Graficar
plt.figure(figsize=(12, 8))
plt.scatter(vectores_2d[:, 0], vectores_2d[:, 1], alpha=0.6, s=20)
for i in range(min(20, len(etiquetas))):
    plt.text(vectores_2d[i, 0], vectores_2d[i, 1], etiquetas[i], fontsize=8)

plt.title("Proyección PCA de embeddings FAISS")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.grid(True)
plt.tight_layout()
plt.savefig("embeddings_2d_plot_1.png")
print("✅ Gráfico guardado como embeddings_2d_plot.png")
