import chromadb


class ChromaInfoService:

    def __init__(self, host="chromadb", port=8000):
        self.client = chromadb.HttpClient(
            host=host,
            port=port
        )

    def listar_colecciones(self, limite=5):

        resultado = []

        colecciones = self.client.list_collections()

        for coleccion in colecciones:

            collection = self.client.get_collection(coleccion.name)

            datos = collection.get(limit=limite)

            registros = []

            for i in range(len(datos["ids"])):
                registros.append({
                    "id": datos["ids"][i],
                    "documento": datos["documents"][i],
                    "metadata": datos["metadatas"][i]
                })

            resultado.append({
                "coleccion": coleccion.name,
                "total_registros": collection.count(),
                "registros": registros
            })

        return {
            "total_colecciones": len(resultado),
            "colecciones": resultado
        }