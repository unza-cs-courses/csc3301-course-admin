# CSC3301 Variant Reference Guide

This document describes what varies per student in each assignment and why.

---

## Variant Generation Principles

### Goals

1. **Prevent Copying:** Students can't directly copy solutions
2. **Fair Assessment:** All variants have equivalent difficulty
3. **Reproducibility:** Same student always gets same variant
4. **Auditability:** Variants can be regenerated for verification

### How It Works

```
Student GitHub Username
         ↓
    SHA256 Hash
         ↓
    Variant Seed
         ↓
  Deterministic Random Generator
         ↓
  Assignment-Specific Parameters
```

---

## Assignment Variants

### Lab 01: Scope and Binding

**Variant Elements:**

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `scope_values.global` | Global scope variable value | "GLOBAL_ALPHA", "GLOBAL_BETA", etc. |
| `scope_values.enclosing` | Enclosing scope value | "ENCLOSING_GAMMA", etc. |
| `scope_values.local` | Local scope value | "LOCAL_DELTA", etc. |
| `counter_tests.initial_values` | Counter starting values | [15, 28, 42] |
| `closure_tests.multiplier_input` | Test input for closures | 5, 7, 10, 12, 15, 20 |
| `introspection_tests.secret_value` | Hidden value for introspection | 10-100 |

**Why These Vary:**
- Different string constants prevent copy-paste
- Different counter values test understanding, not memorization
- Different multipliers verify closure implementation works generally

**Sample Variant Config:**
```json
{
  "student_id": "john_doe",
  "variant_seed": 2847593847,
  "scope_values": {
    "global": "GLOBAL_OMEGA",
    "enclosing": "ENCLOSING_SIGMA",
    "local": "LOCAL_PHI"
  },
  "counter_tests": {
    "initial_values": [23, 41, 8]
  },
  "closure_tests": {
    "multiplier_input": 12,
    "expected_results": [0, 12, 24, 36, 48]
  }
}
```

---

### Lab 02: Type Systems

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `type_annotation_tests.test_values` | Values to annotate |
| `type_checker_tests.valid_assignments` | Correct type assignments |
| `type_checker_tests.invalid_assignments` | Type mismatches to detect |

**Why These Vary:**
- Different test values ensure type checker works generally
- Different invalid cases test error detection comprehensively

---

### Lab 03: Functional Programming

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `hof_tests.test_list` | Input list for map/filter/reduce |
| `hof_tests.filter_threshold` | Cutoff for filter tests |
| `hof_tests.map_multiplier` | Factor for map tests |
| `reduce_tests.numbers` | Numbers for reduce operations |
| `composition_tests.input_value` | Starting value for composition |

**Why These Vary:**
- Different lists prevent hardcoded solutions
- Different thresholds test filter logic, not specific values

---

### Lab 04: OOP Design

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `shape_tests.circle_radius` | Radius for circle calculations |
| `shape_tests.rectangle_width/height` | Rectangle dimensions |
| `shape_tests.triangle_base/height` | Triangle dimensions |
| `pattern_tests.observer_events` | Events to trigger |
| `pattern_tests.factory_types` | Types to create |

**Why These Vary:**
- Different dimensions verify formulas work correctly
- Different events ensure observer pattern is implemented properly

---

### Lab 05: Logic Programming (Prolog)

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `family_facts` | Names in family tree |
| `list_operations.test_lists` | Lists for operations |
| `query_goals` | Goals to prove |

**Why These Vary:**
- Different names prevent sharing knowledge bases
- Different test data verifies predicates work generally

---

### Lab 06: Concurrency

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `threading_tests.num_threads` | Number of concurrent threads |
| `threading_tests.iterations_per_thread` | Operations per thread |
| `async_tests.num_tasks` | Number of async tasks |
| `async_tests.delay_seconds` | Simulated delay |

**Why These Vary:**
- Different thread counts test scalability
- Different iteration counts verify race condition prevention

---

### Project 01: Expression Evaluator

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `required_functions` | Math functions to implement (4-6 of: sqrt, abs, sin, cos, tan, log, exp, floor, ceil) |
| `test_constants` | Specific numeric constants |
| `precision` | Required decimal precision (4-6) |

**Why These Vary:**
- Different required functions prevent code sharing
- Same complexity regardless of which functions assigned
- Tests verify implementation, not memorization

**Sample:**
- Student A: sqrt, abs, sin, cos, floor (5 functions)
- Student B: abs, tan, log, exp, ceil (5 functions)

---

### Project 02: Symbolic Differentiator (Scheme)

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `test_expressions` | Expressions to differentiate |
| `simplification_rules` | Required simplifications |
| `variable_names` | Primary variable (x, y, t, etc.) |

**Why These Vary:**
- Different expressions test derivative rules comprehensively
- Different variable names prevent hardcoded solutions

---

### Project 03: Design Patterns

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `required_patterns` | 4-5 patterns to implement |
| `pattern_scenarios` | Specific use cases |
| `class_names` | Names for pattern classes |

**Why These Vary:**
- Different pattern combinations prevent sharing
- All combinations have equivalent difficulty
- Scenarios test understanding of when to use patterns

**Pattern Pool:**
- Creational: Singleton, Factory, Builder, Prototype
- Structural: Adapter, Decorator, Facade, Proxy
- Behavioral: Observer, Strategy, Command, Iterator

---

### Project 04: Expert System (Prolog)

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `knowledge_domain` | Domain for expert system |
| `fact_sets` | Initial facts |
| `rule_structures` | Rules to implement |
| `query_templates` | Queries to support |

**Why These Vary:**
- Different domains prevent knowledge base sharing
- All domains have equivalent reasoning complexity
- Tests verify inference engine, not domain knowledge

---

### Project 05: Concurrent Pipeline

**Variant Elements:**

| Parameter | Description |
|-----------|-------------|
| `pipeline_config.num_stages` | Number of pipeline stages |
| `pipeline_config.workers_per_stage` | Parallelism level |
| `pipeline_config.buffer_size` | Queue sizes |
| `test_data_size` | Volume of test data |
| `performance_thresholds` | Required throughput/latency |

**Why These Vary:**
- Different stage counts test pipeline flexibility
- Different worker counts test scaling implementation
- Performance thresholds ensure efficient implementation

---

## Verification

### Checking a Student's Variant

```bash
cd submissions/assignment-student_name
cat .variant_config.json
```

### Regenerating a Variant

```bash
python scripts/variant_generator.py student_username
```

The output should match `.variant_config.json` in their repo.

### Verifying Test Compatibility

```bash
# Run tests with explicit variant
VARIANT_CONFIG=.variant_config.json pytest tests/visible/
```

---

## Fairness Analysis

All variants are designed to have:

1. **Same Complexity:** Equal number of concepts to implement
2. **Same Time Requirements:** Equivalent effort to complete
3. **Same Learning Outcomes:** All test the same skills
4. **Same Grading Rubric:** Identical evaluation criteria

If a student believes their variant is unfair, they can request review.
The variant seed is deterministic, so we can verify what they received.

---

## Technical Notes

### Seed Calculation

```python
import hashlib

def compute_seed(assignment_id: str, student_id: str, salt: str = "") -> int:
    combined = f"{assignment_id}:{salt}:{student_id}"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return int.from_bytes(hash_bytes[:8], byteorder='big')
```

### Reproducibility

- Same student ID → Same seed → Same variant
- Different assignment → Different seed (assignment in hash)
- Different semester → Different seed (salt changes)

### Collision Resistance

SHA256 provides sufficient entropy that variant collisions are extremely unlikely.
With ~100 students, probability of identical variants ≈ 0.
