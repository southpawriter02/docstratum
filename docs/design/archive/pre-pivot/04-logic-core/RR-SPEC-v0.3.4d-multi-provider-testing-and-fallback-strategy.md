# Multi-Provider Testing & Fallback Strategy

> **v0.3.4d DocStratum Agent — Logic Core**
> Tests DocStratum agent across multiple LLM providers (OpenAI, Anthropic, Ollama) and implements intelligent fallback strategies when primary providers are unavailable.

## Objective

Design multi-provider testing and fallback strategy that:
- Test same questions across all three LLM providers
- Compare behavioral quality differences between providers
- Identify provider-specific prompt adjustments needed
- Implement fallback chain (primary → secondary → tertiary → cached → error)
- Analyze cost per query for each provider
- Recommend optimal provider for DocStratum context
- Handle provider failures gracefully in production

## Scope Boundaries

**INCLUDES:**
- Testing framework for multiple providers
- Provider-specific prompt adjustments
- Fallback chain implementation and logic
- Model capability matrix (context window, quality, cost)
- Cost analysis and ROI calculations
- Provider recommendation engine
- Complete multi-provider test runner
- Response caching for fallback scenarios

**EXCLUDES:**
- Real cost billing analysis
- Provider contract negotiation
- User interface for provider selection
- Real-time provider health monitoring
- Custom model training

---

## Dependency Diagram

```
Test Question
├── Provider Selection Strategy
│   ├── Primary Provider (OpenAI)
│   ├── Secondary Provider (Anthropic)
│   └── Tertiary Provider (Ollama)
├── Query Execution
│   ├── Time each provider
│   ├── Measure token usage
│   ├── Verify response quality
│   └── Collect AgentResponse
├── Response Comparison
│   ├── Behavioral Verification (BehaviorVerifier)
│   ├── Cost Calculation
│   └── Latency Comparison
└── Fallback Decision
    ├── Primary succeeds: Return response
    ├── Primary fails: Try secondary
    ├── Secondary fails: Try tertiary
    ├── All fail: Return cached response
    └── No cache: Return error
```

---

## 1. Model Capability Matrix

### Complete Provider Comparison

```python
from dataclasses import dataclass
from enum import Enum

class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

@dataclass
class ModelCapabilities:
    """Complete capability data for one model"""
    provider: str
    model_name: str
    context_window: int           # Max tokens
    input_cost_per_1m: float      # Cost per 1M input tokens
    output_cost_per_1m: float     # Cost per 1M output tokens
    quality_score: int            # 1-10 (subjective)
    instruction_following: int    # 1-10
    citation_behavior: int        # 1-10
    few_shot_ability: int         # 1-10
    typical_latency_ms: int       # Average response time
    supports_system_prompt: bool
    max_output_tokens: int
    training_data_cutoff: str

# Define all models
MODEL_MATRIX = {
    "openai_gpt4o_mini": ModelCapabilities(
        provider="openai",
        model_name="gpt-4o-mini",
        context_window=128000,
        input_cost_per_1m=0.15,
        output_cost_per_1m=0.60,
        quality_score=9,
        instruction_following=9,
        citation_behavior=8,
        few_shot_ability=9,
        typical_latency_ms=1500,
        supports_system_prompt=True,
        max_output_tokens=4096,
        training_data_cutoff="April 2024"
    ),

    "anthropic_claude35_sonnet": ModelCapabilities(
        provider="anthropic",
        model_name="claude-3-5-sonnet-20241022",
        context_window=200000,
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        quality_score=10,
        instruction_following=10,
        citation_behavior=10,
        few_shot_ability=10,
        typical_latency_ms=2500,
        supports_system_prompt=True,
        max_output_tokens=4096,
        training_data_cutoff="April 2024"
    ),

    "ollama_mistral": ModelCapabilities(
        provider="ollama",
        model_name="mistral:7b",
        context_window=32768,
        input_cost_per_1m=0.0,      # Local, no API cost
        output_cost_per_1m=0.0,
        quality_score=7,
        instruction_following=7,
        citation_behavior=6,
        few_shot_ability=7,
        typical_latency_ms=500,     # Highly variable by hardware
        supports_system_prompt=True,
        max_output_tokens=2048,
        training_data_cutoff="August 2023"
    ),

    "ollama_llama2": ModelCapabilities(
        provider="ollama",
        model_name="llama2:7b",
        context_window=4096,
        input_cost_per_1m=0.0,
        output_cost_per_1m=0.0,
        quality_score=6,
        instruction_following=6,
        citation_behavior=5,
        few_shot_ability=5,
        typical_latency_ms=400,
        supports_system_prompt=True,
        max_output_tokens=2048,
        training_data_cutoff="July 2023"
    ),
}

# Compatibility check for DocStratum context
def check_provider_compatibility(
    model_key: str,
    context_size_tokens: int = 3000,
    required_quality: int = 7
) -> dict:
    """
    Check if provider can handle DocStratum context.

    Args:
        model_key: Key from MODEL_MATRIX
        context_size_tokens: Size of llms.txt context
        required_quality: Minimum quality score needed

    Returns:
        Dictionary with compatibility check
    """
    model = MODEL_MATRIX.get(model_key)
    if not model:
        return {"compatible": False, "reason": "Model not found"}

    checks = {
        "context_window": model.context_window > context_size_tokens,
        "quality": model.quality_score >= required_quality,
        "citation_behavior": model.citation_behavior >= 6,
        "system_prompt": model.supports_system_prompt,
    }

    compatible = all(checks.values())

    return {
        "compatible": compatible,
        "model": model.model_name,
        "checks": checks,
        "estimated_cost_per_query": estimate_query_cost(model, 500, 200)  # Assume 500 prompt, 200 completion
    }

def estimate_query_cost(model: ModelCapabilities, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost of one query"""
    input_cost = (prompt_tokens / 1_000_000) * model.input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * model.output_cost_per_1m
    return input_cost + output_cost
```

---

## 2. Provider-Specific Prompt Adjustments

### Tailoring Prompts for Each Provider

```python
class ProviderPromptAdapter:
    """Adapt system prompt for specific provider quirks"""

    @staticmethod
    def adapt_for_provider(
        base_prompt: str,
        provider: ProviderType
    ) -> str:
        """
        Adjust prompt based on provider's strengths/weaknesses.

        Strategy: Keep core content same, adjust style/format.
        """

        if provider == ProviderType.OPENAI:
            return ProviderPromptAdapter._adapt_for_openai(base_prompt)
        elif provider == ProviderType.ANTHROPIC:
            return ProviderPromptAdapter._adapt_for_anthropic(base_prompt)
        elif provider == ProviderType.OLLAMA:
            return ProviderPromptAdapter._adapt_for_ollama(base_prompt)
        else:
            return base_prompt

    @staticmethod
    def _adapt_for_openai(prompt: str) -> str:
        """
        OpenAI (GPT-4o mini) is good at following detailed instructions
        and using external references. Keep prompt detailed.

        Strengths: instruction following, breadth
        Style: Direct, clear instructions
        """
        # OpenAI-specific tweaks
        adapted = prompt.replace(
            "BEHAVIORAL RULES",
            "DETAILED INSTRUCTIONS FOR RESPONSES"
        )
        adapted += "\n\nNote: Be conversational but precise. GPT-4o excels at nuance."
        return adapted

    @staticmethod
    def _adapt_for_anthropic(prompt: str) -> str:
        """
        Anthropic Claude excels at reasoning and citations.
        Add explicit citation instructions, reduce redundancy.

        Strengths: reasoning, citations, honesty
        Style: Elaborate reasoning, explicit uncertainty
        """
        adapted = prompt.replace(
            "CITE YOUR SOURCES",
            "CITE YOUR SOURCES IN DETAIL\n   When citing, include the exact URL and relevant section."
        )
        adapted += (
            "\n\nAs Claude, you excel at reasoning through complex problems. "
            "Explain your reasoning step-by-step."
        )
        return adapted

    @staticmethod
    def _adapt_for_ollama(prompt: str) -> str:
        """
        Ollama models (local) are less capable. Simplify prompt,
        add more examples, reduce complexity.

        Strengths: simple tasks, local privacy
        Style: Shorter sentences, explicit examples
        Limitations: context window (32K vs 128K/200K), quality
        """
        # Simplify language
        adapted = prompt.replace(
            "Behavioral rules",
            "Simple rules for responses"
        )

        # Reduce context window estimate in error messages
        adapted += (
            "\n\nNote: For complex queries, you may need to cite "
            "specific URLs from the documentation. If unsure, ask for clarification."
        )

        return adapted
```

### Provider Selection Based on Query

```python
class ProviderSelector:
    """Select best provider for a given query"""

    @staticmethod
    def select_provider(
        question: str,
        context_size_tokens: int,
        prefer_fast: bool = False,
        prefer_cheap: bool = False,
        require_quality: int = 8
    ) -> ProviderType:
        """
        Select provider based on query characteristics.

        Args:
            question: User question
            context_size_tokens: Size of DocStratum context
            prefer_fast: Optimize for latency
            prefer_cheap: Optimize for cost
            require_quality: Minimum quality needed

        Returns:
            ProviderType to use
        """

        # Analyze question complexity
        complexity = len(question.split())
        is_complex = complexity > 50

        # Check quality requirements
        if require_quality >= 9:
            return ProviderType.ANTHROPIC  # Best quality

        if prefer_cheap:
            return ProviderType.OLLAMA  # Free (local)

        if prefer_fast:
            # Ollama is fastest (local) but lower quality
            if require_quality <= 6:
                return ProviderType.OLLAMA
            else:
                return ProviderType.OPENAI

        # Default: OpenAI (good balance)
        return ProviderType.OPENAI

    @staticmethod
    def get_provider_chain() -> list[ProviderType]:
        """
        Get fallback provider chain in order of preference.

        Returns list of providers to try in order.
        """
        return [
            ProviderType.OPENAI,        # Primary: good balance
            ProviderType.ANTHROPIC,     # Secondary: highest quality
            ProviderType.OLLAMA,        # Tertiary: always available (local)
        ]
```

---

## 3. Fallback Chain Implementation

### Intelligent Fallback Strategy

```python
from typing import Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

class FallbackChain:
    """Implement intelligent fallback strategy"""

    def __init__(
        self,
        primary: ProviderType = ProviderType.OPENAI,
        secondary: ProviderType = ProviderType.ANTHROPIC,
        tertiary: ProviderType = ProviderType.OLLAMA,
        cache_dir: str = ".docstratum_cache"
    ):
        self.chain = [primary, secondary, tertiary]
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def invoke_with_fallback(
        self,
        agents: dict,  # Maps ProviderType to DocumentationAgent
        question: str,
        cache_ttl_minutes: int = 60
    ) -> tuple['AgentResponse', ProviderType]:
        """
        Invoke agent with automatic fallback.

        Strategy:
        1. Try primary provider
        2. If fails, try secondary
        3. If fails, try tertiary
        4. If all fail, try cache
        5. If no cache, return error

        Args:
            agents: Dict mapping ProviderType to DocumentationAgent
            question: Question to ask
            cache_ttl_minutes: Cache time-to-live

        Returns:
            (AgentResponse, ProviderType used)
        """

        # Try each provider in chain
        for provider in self.chain:
            if provider not in agents:
                continue

            try:
                response = agents[provider].invoke(question)

                if response.is_success():
                    # Cache successful response
                    self._cache_response(question, response, provider)
                    return response, provider

            except Exception as e:
                # Log failure and continue to next
                print(f"Provider {provider.value} failed: {e}")
                continue

        # All providers failed, try cache
        cached = self._get_cached_response(question, cache_ttl_minutes)
        if cached:
            response, used_provider = cached
            return response, used_provider

        # No response available
        from agent import AgentResponse
        return AgentResponse(
            response="",
            model="unknown",
            provider="fallback",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=0,
            timestamp=datetime.now().isoformat(),
            error="All providers failed and no cached response available"
        ), ProviderType.OPENAI

    def _cache_response(
        self,
        question: str,
        response: 'AgentResponse',
        provider: ProviderType
    ):
        """Cache successful response"""
        import hashlib

        # Create cache key from question hash
        q_hash = hashlib.md5(question.encode()).hexdigest()
        cache_file = self.cache_dir / f"{q_hash}.json"

        cache_data = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "provider": provider.value,
            "response": response.to_dict()
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def _get_cached_response(
        self,
        question: str,
        ttl_minutes: int
    ) -> Optional[tuple['AgentResponse', ProviderType]]:
        """Retrieve cached response if still valid"""
        import hashlib
        from agent import AgentResponse

        q_hash = hashlib.md5(question.encode()).hexdigest()
        cache_file = self.cache_dir / f"{q_hash}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                cache_data = json.load(f)

            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > timedelta(minutes=ttl_minutes):
                return None  # Cache expired

            # Reconstruct response
            response_dict = cache_data['response']
            response = AgentResponse(
                response=response_dict['response'],
                model=response_dict['model'],
                provider=response_dict['provider'],
                prompt_tokens=response_dict['tokens']['prompt'],
                completion_tokens=response_dict['tokens']['completion'],
                total_tokens=response_dict['tokens']['total'],
                latency_ms=response_dict['latency_ms'],
                timestamp=response_dict['timestamp']
            )

            provider = ProviderType[cache_data['provider'].upper()]
            return response, provider

        except Exception as e:
            print(f"Failed to load cache: {e}")
            return None

    def clear_cache(self):
        """Clear all cached responses"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)
```

---

## 4. Multi-Provider Test Runner

### Complete Implementation

```python
from typing import List
from tabulate import tabulate  # pip install tabulate

class MultiProviderTestRunner:
    """Run tests across all providers and compare results"""

    def __init__(self, context_path: str):
        self.context_path = context_path
        self.results = {}

    def run_all_providers(
        self,
        questions: List[str],
        domain_terms: List[str]
    ) -> dict:
        """
        Run same questions across all providers.

        Returns comprehensive comparison results.
        """

        results = {}

        # Test each provider
        for provider_type in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.OLLAMA]:
            print(f"\n{'='*80}")
            print(f"Testing {provider_type.value.upper()}")
            print(f"{'='*80}")

            try:
                provider_results = self._test_provider(
                    provider_type,
                    questions,
                    domain_terms
                )
                results[provider_type.value] = provider_results
            except Exception as e:
                print(f"Error testing {provider_type.value}: {e}")
                results[provider_type.value] = {"error": str(e)}

        return results

    def _test_provider(
        self,
        provider: ProviderType,
        questions: List[str],
        domain_terms: List[str]
    ) -> dict:
        """Test single provider"""

        from v0_3_4a import create_docstratum_agent
        from v0_3_4b import BehaviorVerifier

        # Create agent for this provider
        agent = create_docstratum_agent(
            context_path=self.context_path,
            provider=provider.value.lower()
        )

        verifier = BehaviorVerifier(domain_terms)
        provider_results = []

        # Test each question
        for question in questions:
            print(f"  Q: {question[:60]}...")

            response = agent.invoke(question)

            if not response.is_success():
                print(f"    ERROR: {response.error}")
                continue

            behavior = verifier.analyze(response)

            provider_results.append({
                "question": question,
                "response": response,
                "behavior": behavior,
                "cost": self._estimate_cost(response, provider)
            })

            print(f"    Score: {behavior.overall_score:.1f}/5.0 | "
                  f"Tokens: {response.total_tokens} | "
                  f"Cost: ${self._estimate_cost(response, provider):.4f}")

        return {
            "results": provider_results,
            "avg_score": sum(r['behavior'].overall_score for r in provider_results) / len(provider_results) if provider_results else 0,
            "total_cost": sum(r['cost'] for r in provider_results),
            "avg_latency_ms": sum(r['response'].latency_ms for r in provider_results) / len(provider_results) if provider_results else 0
        }

    def _estimate_cost(self, response: 'AgentResponse', provider: ProviderType) -> float:
        """Estimate cost of response"""
        model_key = self._get_model_key(provider)
        model = MODEL_MATRIX.get(model_key)

        if not model:
            return 0.0

        return estimate_query_cost(
            model,
            response.prompt_tokens,
            response.completion_tokens
        )

    def _get_model_key(self, provider: ProviderType) -> str:
        """Get default model key for provider"""
        defaults = {
            ProviderType.OPENAI: "openai_gpt4o_mini",
            ProviderType.ANTHROPIC: "anthropic_claude35_sonnet",
            ProviderType.OLLAMA: "ollama_mistral"
        }
        return defaults.get(provider, "openai_gpt4o_mini")

    def generate_comparison_report(self, all_results: dict) -> str:
        """Generate comparison table"""

        report = "\n\nMULTI-PROVIDER COMPARISON REPORT\n"
        report += "=" * 80 + "\n\n"

        # Create comparison table
        rows = []
        for provider, data in all_results.items():
            if "error" in data:
                rows.append([provider, "ERROR", "—", "—", "—"])
            else:
                rows.append([
                    provider,
                    f"{data['avg_score']:.2f}/5.0",
                    f"{data['avg_latency_ms']:.0f}ms",
                    f"${data['total_cost']:.2f}",
                    f"{len(data['results'])} tests"
                ])

        headers = ["Provider", "Avg Score", "Avg Latency", "Total Cost", "Tests"]
        report += tabulate(rows, headers=headers, tablefmt="grid")

        return report
```

---

## 5. Cost Analysis per Provider

### ROI and Cost Calculations

```python
class CostAnalyzer:
    """Analyze cost implications of provider choice"""

    @staticmethod
    def calculate_annual_cost(
        monthly_queries: int,
        avg_prompt_tokens: int,
        avg_completion_tokens: int,
        provider: str  # "openai", "anthropic", "ollama"
    ) -> dict:
        """
        Calculate annual costs for one provider.

        Args:
            monthly_queries: Number of API calls per month
            avg_prompt_tokens: Average prompt token count
            avg_completion_tokens: Average completion token count
            provider: Provider name

        Returns:
            Cost breakdown
        """

        annual_queries = monthly_queries * 12

        # Get model
        model_key = {
            "openai": "openai_gpt4o_mini",
            "anthropic": "anthropic_claude35_sonnet",
            "ollama": "ollama_mistral"
        }.get(provider)

        model = MODEL_MATRIX.get(model_key)

        if not model:
            return {"error": "Unknown provider"}

        # Calculate costs
        annual_input_tokens = annual_queries * avg_prompt_tokens
        annual_output_tokens = annual_queries * avg_completion_tokens

        annual_input_cost = (annual_input_tokens / 1_000_000) * model.input_cost_per_1m
        annual_output_cost = (annual_output_tokens / 1_000_000) * model.output_cost_per_1m
        total_annual_cost = annual_input_cost + annual_output_cost

        return {
            "provider": provider,
            "annual_queries": annual_queries,
            "annual_input_tokens": annual_input_tokens,
            "annual_output_tokens": annual_output_tokens,
            "annual_input_cost": annual_input_cost,
            "annual_output_cost": annual_output_cost,
            "total_annual_cost": total_annual_cost,
            "cost_per_query": total_annual_cost / annual_queries if annual_queries > 0 else 0
        }

    @staticmethod
    def compare_providers(
        monthly_queries: int,
        avg_prompt_tokens: int = 500,
        avg_completion_tokens: int = 200
    ) -> dict:
        """
        Compare annual costs across all providers.

        Returns ordered list of providers by cost.
        """

        results = []

        for provider in ["openai", "anthropic", "ollama"]:
            cost_data = CostAnalyzer.calculate_annual_cost(
                monthly_queries,
                avg_prompt_tokens,
                avg_completion_tokens,
                provider
            )
            results.append(cost_data)

        # Sort by annual cost
        results.sort(key=lambda x: x['total_annual_cost'])

        return results

    @staticmethod
    def generate_cost_report(
        monthly_queries: int,
        results: dict
    ) -> str:
        """Generate cost comparison report"""

        report = f"\n\nCOST ANALYSIS REPORT\n"
        report += "=" * 80 + "\n"
        report += f"Assumptions: {monthly_queries} queries/month, 500 prompt tokens, 200 completion tokens\n\n"

        comparison = CostAnalyzer.compare_providers(
            monthly_queries,
            500,
            200
        )

        rows = []
        for data in comparison:
            rows.append([
                data['provider'],
                f"${data['cost_per_query']:.4f}",
                f"${data['total_annual_cost']:.2f}",
                f"{data['total_annual_cost'] / comparison[0]['total_annual_cost']:.1f}x base"
            ])

        headers = ["Provider", "Cost/Query", "Annual Cost", "Relative to Cheapest"]
        report += tabulate(rows, headers=headers, tablefmt="grid")

        return report
```

---

## 6. Provider Recommendation Engine

### Intelligent Selection

```python
class ProviderRecommender:
    """Recommend best provider based on requirements"""

    SCENARIOS = {
        "best_quality": {
            "description": "Need highest quality responses",
            "priority": ["quality", "instruction_following", "citation_behavior"],
            "min_quality": 9
        },
        "cost_optimized": {
            "description": "Minimize API costs",
            "priority": ["cost", "quality"],
            "min_quality": 6
        },
        "balanced": {
            "description": "Balance cost and quality",
            "priority": ["quality", "cost", "latency"],
            "min_quality": 8
        },
        "fast_response": {
            "description": "Minimize response latency",
            "priority": ["latency", "quality"],
            "min_quality": 7
        },
        "local_only": {
            "description": "Keep data local, no external APIs",
            "priority": ["privacy"],
            "min_quality": 5
        }
    }

    @staticmethod
    def recommend(
        scenario: str,
        monthly_queries: int = 1000
    ) -> tuple[str, dict]:
        """
        Recommend provider for specific scenario.

        Args:
            scenario: One of the scenarios above
            monthly_queries: Expected monthly query volume

        Returns:
            (provider_name, detailed_recommendation)
        """

        if scenario not in ProviderRecommender.SCENARIOS:
            return "openai", {"error": f"Unknown scenario: {scenario}"}

        scenario_config = ProviderRecommender.SCENARIOS[scenario]

        # Score each provider
        scores = {}

        for provider_key, model in MODEL_MATRIX.items():
            provider = model.provider
            if provider not in scores:
                scores[provider] = 0

            # Score based on priority factors
            for factor in scenario_config['priority']:
                if factor == "quality":
                    scores[provider] += model.quality_score * 10
                elif factor == "cost":
                    annual_cost = CostAnalyzer.calculate_annual_cost(
                        monthly_queries, 500, 200, provider
                    )['total_annual_cost']
                    # Lower cost = higher score (invert)
                    scores[provider] += max(0, 100 - annual_cost)
                elif factor == "latency":
                    # Lower latency = higher score (invert)
                    scores[provider] += max(0, 1000 - model.typical_latency_ms)
                elif factor == "privacy":
                    # Only Ollama has full privacy
                    if provider == "ollama":
                        scores[provider] += 100

        # Get best provider
        best_provider = max(scores.items(), key=lambda x: x[1])

        return best_provider[0], {
            "scenario": scenario,
            "description": scenario_config['description'],
            "recommended": best_provider[0],
            "reasoning": f"Optimized for: {', '.join(scenario_config['priority'])}",
            "scores": scores,
            "cost_estimate": CostAnalyzer.calculate_annual_cost(
                monthly_queries, 500, 200, best_provider[0]
            )
        }
```

---

## 7. Complete Multi-Provider Test Implementation

### pytest Test Suite

```python
# tests/test_multi_provider.py
import pytest
from v0_3_4d import (
    MultiProviderTestRunner,
    FallbackChain,
    ProviderRecommender,
    CostAnalyzer
)

class TestMultiProvider:
    """Test multi-provider functionality"""

    @pytest.fixture
    def test_questions(self):
        return [
            "What is this system?",
            "How do I get started?",
            "What are common mistakes?"
        ]

    @pytest.fixture
    def domain_terms(self):
        return ["API", "authentication", "middleware"]

    def test_provider_selector(self):
        """Test provider selection logic"""
        from v0_3_4d import ProviderSelector, ProviderType

        # Complex query with high quality requirement
        provider = ProviderSelector.select_provider(
            "This is a very complex question about advanced usage patterns",
            context_size_tokens=3000,
            require_quality=9
        )
        assert provider == ProviderType.ANTHROPIC

        # Fast response needed
        provider = ProviderSelector.select_provider(
            "Quick question",
            context_size_tokens=3000,
            prefer_fast=True
        )
        assert provider == ProviderType.OLLAMA

    def test_fallback_chain(self):
        """Test fallback chain selection"""
        from v0_3_4d import ProviderSelector

        chain = ProviderSelector.get_provider_chain()

        assert len(chain) >= 2
        # First in chain should be OpenAI
        assert chain[0].value == "openai"

    def test_cost_comparison(self):
        """Test cost analysis"""
        costs = CostAnalyzer.compare_providers(
            monthly_queries=1000,
            avg_prompt_tokens=500,
            avg_completion_tokens=200
        )

        assert len(costs) >= 2
        # First should be cheapest
        assert costs[0]['total_annual_cost'] <= costs[-1]['total_annual_cost']

    def test_provider_recommendation(self):
        """Test provider recommendation"""
        provider, rec = ProviderRecommender.recommend(
            scenario="best_quality"
        )

        assert provider in ["openai", "anthropic", "ollama"]
        assert "recommended" in rec

    def test_capability_matrix(self):
        """Test model capability definitions"""
        from v0_3_4d import MODEL_MATRIX

        # All models should have required fields
        for model_key, model in MODEL_MATRIX.items():
            assert model.context_window > 0
            assert model.quality_score > 0
            assert model.typical_latency_ms > 0
```

---

## Deliverables

1. **ModelCapabilities dataclass** and complete MODEL_MATRIX
2. **ProviderPromptAdapter** for provider-specific tweaks
3. **ProviderSelector** for intelligent provider selection
4. **FallbackChain** implementation with caching
5. **MultiProviderTestRunner** complete test suite
6. **CostAnalyzer** for ROI calculations
7. **ProviderRecommender** recommendation engine
8. **Complete pytest test suite** for multi-provider testing

---

## Acceptance Criteria

- [ ] MODEL_MATRIX defines all three providers with accurate specs
- [ ] ProviderPromptAdapter produces valid adjusted prompts
- [ ] ProviderSelector correctly chooses provider based on constraints
- [ ] FallbackChain successfully tries providers in order
- [ ] FallbackChain caches responses for offline use
- [ ] MultiProviderTestRunner tests all three providers
- [ ] Cost analysis accurately calculates annual expenses
- [ ] ProviderRecommender recommends appropriate provider per scenario
- [ ] All 10+ multi-provider tests pass
- [ ] Cost report shows clear comparison between providers
- [ ] Prompt adjustments maintain behavioral integrity across providers

---

## Conclusion

These 8 comprehensive documents (4 for v0.3.3 Baseline Agent + 4 for v0.3.4 DocStratum Agent) establish the complete "Logic Core" for the DocStratum project's Platinum Standard llms.txt architecture. The framework enables:

✓ **Baseline control group** (v0.3.3) with generic agent
✓ **DocStratum enhancement** (v0.3.4) with context injection
✓ **Fair comparison** through identical architecture
✓ **Multi-provider support** across OpenAI, Anthropic, Ollama
✓ **Behavioral verification** through 5 key quality signals
✓ **Integration testing** with end-to-end pipeline
✓ **Production resilience** through fallback chains and caching
✓ **Cost optimization** through provider selection and analysis

Each document includes 300-500 lines with H1 headers, blockquotes, objectives, scope boundaries, dependency diagrams, 4-6 numbered sections with tables/code, deliverables, acceptance criteria, and next steps forming a complete reference architecture.
