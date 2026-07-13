import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

colecciones = client.list_collections()

for c in colecciones:
    print(f"\nColección: {c.name}")

    collection = client.get_collection(c.name)
    print("Total:", collection.count())

    datos = collection.get(limit=5)

    for i in range(len(datos["ids"])):
        print("----------------")
        print("ID:", datos["ids"][i])
        print("Documento:", datos["documents"][i])
        print("Metadata:", datos["metadatas"][i])