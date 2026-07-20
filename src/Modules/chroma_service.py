import chromadb
from chromadb.errors import IDAlreadyExistsError
import os
#from chromadb.config import Settings
#from pathlib import Path

class ChromaService:
    def __init__(self, path=None, collection_prefix="stori"):
        ''' 
        #Esto actualmente no se usa ya que la DB esta corriendo en docker y no en local
        #En path=None, se crea la DB en la ruta por defecto de ChromaDB
        
        if path is None:
            path = Path(__file__).resolve().parents[2] / "chroma_db"
        '''
        
        '''
        self.client = chromadb.HttpClient( #Se modifico esta parte para poder tener chroma en un contenedor docker
            host="localhost",
            port=8000
        )
        '''
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", 8000))

        self.client = chromadb.HttpClient(
            host=host,
            port=port
        )
        
        self.collection_prefix = collection_prefix

    def get_collection_name(self, domain: str) -> str:
        domain = str(domain).strip().lower().replace(" ", "_")
        return f"{self.collection_prefix}_{domain}"

    def get_or_create_collection(self, domain: str):
        collection_name = self.get_collection_name(domain)
        return self.client.get_or_create_collection(name=collection_name)

    def get_collection(self, domain: str):
        collection_name = self.get_collection_name(domain)
        try:
            return self.client.get_collection(name=collection_name)
        except Exception as exc:
            raise ValueError(
                f"No existe una colección para el dominio '{domain}' "
                f"({collection_name})."
            ) from exc

    def add_embeddings(
        self,
        domain: str,
        ids: list,
        documents: list,
        embeddings: list,
        metadatas: list,
        batch_size: int = 100
    ):

        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("Todos los arreglos deben tener la misma longitud.")

        collection = self.get_or_create_collection(domain)

        total = len(ids)
        inserted = 0
        failed_batches = []

        for start in range(0, total, batch_size):
            end = start + batch_size

            batch_ids = ids[start:end]
            batch_documents = documents[start:end]
            batch_embeddings = embeddings[start:end]
            batch_metadatas = metadatas[start:end]

            try:
                collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                inserted += len(batch_ids)

            except IDAlreadyExistsError as e:
                failed_batches.append({
                    "batch": f"{start}:{min(end, total)}",
                    "error": f"IDs duplicados: {str(e)}"
                })

            except Exception as e:
                failed_batches.append({
                    "batch": f"{start}:{min(end, total)}",
                    "error": str(e)
                })

        return {
            "domain": domain,
            "collection": self.get_collection_name(domain),
            "total_received": total,
            "inserted": inserted,
            "failed_batches": failed_batches
        }

    def count(self, domain: str) -> int:
        collection = self.get_or_create_collection(domain)
        return collection.count()

    def search_embeddings(
        self,
        domain,
        embedding,
        n_results=5
    ):
        collection = self.get_collection(domain)
        
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()
        
        total = collection.count()
        if total == 0:
            raise ValueError(
                f"La colección del dominio '{domain}' no contiene embeddings."
            )

        n_results = min(n_results, total)
        
        parametros = {
            "query_embeddings": [embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }

        return collection.query(**parametros)
