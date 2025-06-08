#!/usr/bin/env python3
"""
Test script for PM-007 Knowledge Hierarchy Enhancement
Tests the new relationship analysis capabilities
"""
import asyncio
import sys
import os
sys.path.append('.')

from services.knowledge_graph.ingestion import get_ingester

async def test_enhanced_knowledge_hierarchy():
    """Test the enhanced knowledge hierarchy system"""
    
    print("🧪 Testing Enhanced Knowledge Hierarchy (PM-007)")
    print("=" * 60)
    
    ingester = get_ingester()
    
    # Test 1: Basic search functionality
    print("\n📋 Test 1: Basic Search Functionality")
    try:
        results = await ingester.search("login mobile app", n_results=3)
        print(f"✅ Basic search returned {len(results)} results")
        
        if results:
            first_result = results[0]
            metadata = first_result.get('metadata', {})
            print(f"   Sample metadata keys: {list(metadata.keys())}")
            
            # Check for relationship analysis fields
            if 'relationship_analysis_version' in metadata:
                print(f"   ✅ Relationship analysis present: v{metadata['relationship_analysis_version']}")
                print(f"   Document type: {metadata.get('document_type', 'unknown')}")
                print(f"   Hierarchy level: {metadata.get('hierarchy_level', 'unknown')}")
                print(f"   Main concepts: {metadata.get('main_concepts', [])}")
            else:
                print("   ⚠️  No relationship analysis found - documents may need re-ingestion")
    
    except Exception as e:
        print(f"   ❌ Basic search failed: {e}")
    
    # Test 2: Context-aware search
    print("\n📋 Test 2: Context-Aware Search")
    try:
        context_results = await ingester.search_with_context(
            "authentication issues", 
            hierarchy_preference=3,
            n_results=2
        )
        print(f"✅ Context-aware search returned {len(context_results)} results")
        
        if context_results:
            for i, result in enumerate(context_results):
                rel_score = result.get('relationship_score', 0)
                combined_score = result.get('combined_score', 0)
                print(f"   Result {i+1}: rel_score={rel_score:.2f}, combined_score={combined_score:.2f}")
    
    except Exception as e:
        print(f"   ❌ Context-aware search failed: {e}")
    
    # Test 3: Check collection status
    print("\n📋 Test 3: Collection Status")
    try:
        collection = ingester.collection
        doc_count = collection.count()
        print(f"✅ Collection contains {doc_count} documents")
        
        # Sample a few documents to check metadata
        if doc_count > 0:
            sample_results = collection.get(limit=3)
            if sample_results['metadatas']:
                enhanced_count = sum(1 for meta in sample_results['metadatas'] 
                                   if 'relationship_analysis_version' in meta)
                print(f"   {enhanced_count}/{len(sample_results['metadatas'])} sampled docs have relationship analysis")
    
    except Exception as e:
        print(f"   ❌ Collection status check failed: {e}")
    
    print("\n🎯 PM-007 Enhancement Test Complete!")
    print("\nNext Steps:")
    print("1. If no relationship analysis found, re-ingest documents with: python -c \"from services.knowledge_graph.ingestion import get_ingester; import asyncio; asyncio.run(get_ingester().ingest_pdf('your_file.pdf'))\"")
    print("2. Test enhanced search in your main application")
    print("3. Check that intent classification uses the improved context")

if __name__ == "__main__":
    asyncio.run(test_enhanced_knowledge_hierarchy())
