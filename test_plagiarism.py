"""
Test script for plagiarism checker
Run this to verify the plagiarism checker is working correctly
"""
import requests
import os

# Test the plagiarism checker endpoint
def test_plagiarism_checker():
    url = "http://localhost:8000/check-plagiarism/"
    
    # Test with existing document
    test_file = "uploads/ieee_paper.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        print("Please generate a paper first or specify a different .docx file")
        return
    
    print(f"📄 Testing plagiarism checker with: {test_file}")
    print(f"🌐 Endpoint: {url}")
    print("-" * 50)
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(url, files=files)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("📊 PLAGIARISM ANALYSIS REPORT")
            print("="*60)
            
            # Overall Assessment
            print(f"\n🎯 Overall Status: {result.get('overall_status', 'N/A')}")
            print(f"   {result.get('status_message', 'N/A')}")
            print(f"\n📈 Plagiarism Score: {result.get('plagiarism_percentage', 'N/A')}%")
            
            # Statistics
            print(f"\n📋 Document Statistics:")
            print(f"   • Total Words: {result.get('word_count', 'N/A'):,}")
            print(f"   • Total Sentences: {result.get('total_sentences', 'N/A')}")
            print(f"   • Plagiarized Sentences: {result.get('plagiarized_sentence_count', 'N/A')}")
            
            stats = result.get('statistics', {})
            print(f"   • Duplicate Pairs Found: {stats.get('duplicate_pairs_found', 'N/A')}")
            print(f"   • Citations: {stats.get('unique_citations', 'N/A')}")
            print(f"   • References: {stats.get('total_references', 'N/A')}")
            
            # Insights
            insights = result.get('insights', [])
            if insights:
                print(f"\n💡 Insights & Recommendations:")
                for i, insight in enumerate(insights, 1):
                    print(f"   {i}. {insight}")
            
            # Similar sentences preview
            similar = result.get('similar_sentences', [])
            if similar:
                print(f"\n⚠️  Found {len(similar)} similar sentence pair(s):")
                for i, pair in enumerate(similar[:2], 1):  # Show first 2
                    print(f"\n   Pair {i} (Similarity: {pair['similarity']*100:.1f}%):")
                    print(f"   → {pair['sentence_1'][:100]}...")
                    print(f"   → {pair['sentence_2'][:100]}...")
            
            print("\n" + "="*60)
            print("✅ Plagiarism checker is working correctly!")
            print("="*60)
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server is not running!")
        print("   Please start the server with: uvicorn app:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_plagiarism_checker()
