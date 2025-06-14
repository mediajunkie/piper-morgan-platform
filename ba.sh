# Test knowledge search specifically
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from services.knowledge_graph.ingestion import get_ingester
import asyncio

async def test():
    knowledge = get_ingester()
    results = await knowledge.search('GitHub issue best practices', n_results=2)
    print(f'✅ Knowledge search returned {len(results)} results')

asyncio.run(test())
"
