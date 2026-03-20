# GSoC 2026 Proposal: Editing of QTI Question Types in Kolibri Studio

## Personal Details

| Field | Details |
|-------|---------|
| **Full Name** | [YOUR NAME] |
| **Email** | [YOUR EMAIL] |
| **GitHub** | [YOUR GITHUB USERNAME] |
| **LinkedIn** | [YOUR LINKEDIN - optional] |
| **Location & Timezone** | [YOUR LOCATION, e.g., "Mumbai, India (UTC+5:30)"] |
| **University** | [YOUR UNIVERSITY] |
| **Program & Year** | [e.g., "B.Tech Computer Science, 3rd Year"] |

---

## Synopsis

This project aims to create authoring tools in Kolibri Studio for QTI 3.0 question types, enabling content creators to build assessments directly within Studio rather than importing pre-existing QTI packages. Currently, Studio supports basic question types (single/multiple selection, true/false, numeric input) but lacks support for more sophisticated QTI 3.0 interactions such as **inline choice**, **match interaction**, **order interaction**, and **gap match (drag-and-drop)**.

I will implement a complete authoring pipeline that includes:
1. **Vue.js components** for each new interaction type's editing UI
2. **Pydantic models** for validating QTI XML structure
3. **XML generation logic** that produces QTI 3.0 compliant output
4. **API endpoints** for CRUD operations on complex question data
5. **Comprehensive test coverage** ensuring Kolibri viewer compatibility

The solution will extend Studio's existing patterns—using JSON as an intermediate format for question data, converting to QTI XML during export—to maintain consistency with the current architecture while enabling powerful new assessment capabilities.

---

## Benefits to the Community

### For Content Creators
- **Richer Assessments**: Authors can create engaging question types like matching exercises, sequencing tasks, and fill-in-the-blank with dropdowns—all without leaving Studio
- **No External Tools Required**: Eliminates the need for third-party QTI authoring tools, reducing the technical barrier for educators
- **Immediate Preview**: Authors can test their questions within Studio before publishing to Kolibri

### For Learners
- **Diverse Learning Experiences**: Different question types engage different cognitive skills—ordering tests sequential reasoning, matching tests association, gap-fill tests contextual understanding
- **Accessibility**: QTI 3.0's built-in accessibility features (ARIA labels, keyboard navigation) will be properly generated

### For the Kolibri Ecosystem
- **Standards Compliance**: Full QTI 3.0 support positions Kolibri as a serious player in the educational technology space
- **Interoperability**: Content created in Studio can be exported and used in other QTI-compliant systems
- **Foundation for Future Work**: The architecture established here can support additional QTI interaction types in the future

---

## Current Status of the Project

### What Already Exists

After extensive exploration of the Kolibri Studio codebase, I found that significant QTI infrastructure is already in place:

**Frontend (Vue.js 2.7 + Vuex):**
- `AssessmentItemEditor.vue` - Container for editing individual questions
- `AnswersEditor.vue` - Component for managing answer choices with TipTapEditor integration
- `HintsEditor.vue` - Component for managing hints
- Validation utilities in `shared/utils/validation.js`
- `AssessmentItemTypes` constants: `single_selection`, `multiple_selection`, `true_false`, `input_question`

**Backend (Django + DRF):**
- `AssessmentItem` model (`models.py:3033`) storing question data as JSON strings
- API viewsets for CRUD operations with bulk support
- `QTIExerciseGenerator` class (`utils/assessment/qti/archive.py`) for XML generation

**QTI Pydantic Models (`utils/assessment/qti/`):**
- `AssessmentItem` - Root QTI element with response/outcome declarations
- `ChoiceInteraction` - For single/multiple selection questions
- `TextEntryInteraction` - For numeric input questions
- `ResponseDeclaration`, `ResponseProcessing` - For scoring configuration
- HTML and MathML validators for rich content

### What's Missing (Scope of This Project)

| Component | Current State | Required Work |
|-----------|--------------|---------------|
| **Inline Choice** | Not implemented | Full implementation |
| **Match Interaction** | Not implemented | Full implementation |
| **Order Interaction** | Not implemented | Full implementation |
| **Gap Match** | Not implemented | Full implementation |
| **Text Entry (strings)** | Only numeric | Extend for string answers |
| **Authoring UI** | Basic types only | New components per type |

---

## Goals

### Primary Goals
1. Implement authoring UI and QTI generation for **6 interaction types**:
   - Choice Interaction (True/False enhancement)
   - Text Entry (extended for strings)
   - Inline Choice
   - Order Interaction
   - Match Interaction
   - Gap Match Interaction

2. Ensure **100% compatibility** with Kolibri's QTI viewer plugin

3. Maintain **consistency** with Studio's existing patterns and code style

### Secondary Goals
1. Create reusable components that can be extended for future interaction types
2. Document the QTI authoring architecture for future contributors
3. Add comprehensive test coverage (unit, integration, e2e)

---

## Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Order Interaction Editor** | Vue component + Pydantic model + XML generation |
| 2 | **Text Entry Enhancement** | String support with case-sensitivity options |
| 3 | **Inline Choice Editor** | Rich text integration with dropdown markers |
| 4 | **Match Interaction Editor** | Two-column matching interface |
| 5 | **Gap Match Editor** | Drag-and-drop authoring with gap markers |
| 6 | **Test Suite** | Unit tests, integration tests, Kolibri viewer tests |
| 7 | **Documentation** | Architecture docs and contributor guide |

---

## QTI XML Generation Strategy

For each interaction type, I detail the authoring inputs, generated XML structure, response processing, and validation rules.

### 1. Order Interaction

**Description**: Learner arranges items in the correct sequence.

**Authoring UI Inputs:**
- Prompt text (rich text)
- List of orderable items (rich text each)
- Correct order (defined by item arrangement in editor)
- Shuffle option (boolean)
- Orientation (vertical/horizontal)

**Generated XML Structure:**
```xml
<qti-assessment-item xmlns="http://www.imsglobal.org/xsd/imsqtiasi_v3p0"
    identifier="order-q1" title="Sequence Question" adaptive="false">

    <qti-response-declaration identifier="RESPONSE"
        cardinality="ordered" base-type="identifier">
        <qti-correct-response>
            <qti-value>STEP_1</qti-value>
            <qti-value>STEP_2</qti-value>
            <qti-value>STEP_3</qti-value>
        </qti-correct-response>
    </qti-response-declaration>

    <qti-outcome-declaration identifier="SCORE"
        cardinality="single" base-type="float">
        <qti-default-value><qti-value>0</qti-value></qti-default-value>
    </qti-outcome-declaration>

    <qti-item-body>
        <qti-order-interaction response-identifier="RESPONSE"
            shuffle="true" orientation="vertical">
            <qti-prompt>Arrange the steps in chronological order.</qti-prompt>
            <qti-simple-choice identifier="STEP_2">Mix the ingredients</qti-simple-choice>
            <qti-simple-choice identifier="STEP_1">Gather materials</qti-simple-choice>
            <qti-simple-choice identifier="STEP_3">Bake at 350°F</qti-simple-choice>
        </qti-order-interaction>
    </qti-item-body>

    <qti-response-processing
        template="https://purl.imsglobal.org/spec/qti/v3p0/rptemplates/match_correct"/>
</qti-assessment-item>
```

**Response Processing**: Uses `match_correct` template—full credit only if order matches exactly.

**Validation Rules:**
- Minimum 2 items required
- Each item must have non-empty content
- No duplicate identifiers

**JSON Intermediate Format:**
```json
{
  "type": "order_interaction",
  "question": "<p>Arrange the steps in chronological order.</p>",
  "shuffle": true,
  "orientation": "vertical",
  "items": [
    {"identifier": "STEP_1", "content": "Gather materials", "order": 1},
    {"identifier": "STEP_2", "content": "Mix the ingredients", "order": 2},
    {"identifier": "STEP_3", "content": "Bake at 350°F", "order": 3}
  ]
}
```

---

### 2. Text Entry Interaction (Enhanced)

**Description**: Learner types text into a blank within a sentence.

**Authoring UI Inputs:**
- Question text with blank marker(s)
- Accepted answers (multiple allowed)
- Case sensitivity toggle
- Partial credit mapping (optional)

**Generated XML Structure:**
```xml
<qti-assessment-item identifier="textentry-q1" title="Fill in the Blank">

    <qti-response-declaration identifier="RESPONSE"
        cardinality="single" base-type="string">
        <qti-correct-response>
            <qti-value>photosynthesis</qti-value>
        </qti-correct-response>
        <qti-mapping default-value="0" lower-bound="0" upper-bound="1">
            <qti-map-entry map-key="photosynthesis" mapped-value="1" case-sensitive="false"/>
            <qti-map-entry map-key="photo synthesis" mapped-value="0.5" case-sensitive="false"/>
            <qti-map-entry map-key="Photo-synthesis" mapped-value="0.5" case-sensitive="false"/>
        </qti-mapping>
    </qti-response-declaration>

    <qti-outcome-declaration identifier="SCORE" cardinality="single" base-type="float"/>

    <qti-item-body>
        <p>The process by which plants convert sunlight to energy is called
            <qti-text-entry-interaction response-identifier="RESPONSE"
                expected-length="15"/>.</p>
    </qti-item-body>

    <qti-response-processing>
        <qti-set-outcome-value identifier="SCORE">
            <qti-map-response identifier="RESPONSE"/>
        </qti-set-outcome-value>
    </qti-response-processing>
</qti-assessment-item>
```

**Validation Rules:**
- At least one correct answer required
- `expected-length` computed from longest accepted answer

---

### 3. Inline Choice Interaction

**Description**: Learner selects from dropdown menus embedded in text.

**Authoring UI Inputs:**
- Rich text with inline choice markers (inserted via toolbar button)
- For each marker: list of choices with one marked correct
- Shuffle option per dropdown

**Generated XML Structure:**
```xml
<qti-assessment-item identifier="inlinechoice-q1" title="Inline Choice Question">

    <qti-response-declaration identifier="RESPONSE_1"
        cardinality="single" base-type="identifier">
        <qti-correct-response>
            <qti-value>PARIS</qti-value>
        </qti-correct-response>
    </qti-response-declaration>

    <qti-response-declaration identifier="RESPONSE_2"
        cardinality="single" base-type="identifier">
        <qti-correct-response>
            <qti-value>FRANCE</qti-value>
        </qti-correct-response>
    </qti-response-declaration>

    <qti-outcome-declaration identifier="SCORE" cardinality="single" base-type="float"/>

    <qti-item-body>
        <p>The city of
            <qti-inline-choice-interaction response-identifier="RESPONSE_1" shuffle="true">
                <qti-inline-choice identifier="PARIS">Paris</qti-inline-choice>
                <qti-inline-choice identifier="LONDON">London</qti-inline-choice>
                <qti-inline-choice identifier="BERLIN">Berlin</qti-inline-choice>
            </qti-inline-choice-interaction>
        is the capital of
            <qti-inline-choice-interaction response-identifier="RESPONSE_2" shuffle="true">
                <qti-inline-choice identifier="FRANCE">France</qti-inline-choice>
                <qti-inline-choice identifier="GERMANY">Germany</qti-inline-choice>
                <qti-inline-choice identifier="UK">United Kingdom</qti-inline-choice>
            </qti-inline-choice-interaction>.
        </p>
    </qti-item-body>

    <qti-response-processing>
        <qti-response-condition>
            <qti-response-if>
                <qti-and>
                    <qti-match>
                        <qti-variable identifier="RESPONSE_1"/>
                        <qti-correct identifier="RESPONSE_1"/>
                    </qti-match>
                    <qti-match>
                        <qti-variable identifier="RESPONSE_2"/>
                        <qti-correct identifier="RESPONSE_2"/>
                    </qti-match>
                </qti-and>
                <qti-set-outcome-value identifier="SCORE">
                    <qti-base-value base-type="float">1</qti-base-value>
                </qti-set-outcome-value>
            </qti-response-if>
        </qti-response-condition>
    </qti-response-processing>
</qti-assessment-item>
```

**TipTap Integration:**
Custom TipTap node `InlineChoiceNode` that renders as a pill/chip showing "[Dropdown: 3 choices]" in edit mode.

**Validation Rules:**
- Each inline choice must have ≥2 options
- Exactly one correct answer per dropdown
- Unique identifiers across all dropdowns

---

### 4. Match Interaction

**Description**: Learner connects items from two sets (e.g., terms to definitions).

**Authoring UI Inputs:**
- Prompt text
- Source set (left column items)
- Target set (right column items)
- Correct associations (which source maps to which target)
- `match-max` per item (how many times each can be used)
- Shuffle options

**Generated XML Structure:**
```xml
<qti-assessment-item identifier="match-q1" title="Matching Question">

    <qti-response-declaration identifier="RESPONSE"
        cardinality="multiple" base-type="directedPair">
        <qti-correct-response>
            <qti-value>COUNTRY_FR CAPITAL_PARIS</qti-value>
            <qti-value>COUNTRY_DE CAPITAL_BERLIN</qti-value>
            <qti-value>COUNTRY_ES CAPITAL_MADRID</qti-value>
        </qti-correct-response>
        <qti-mapping default-value="0" lower-bound="0">
            <qti-map-entry map-key="COUNTRY_FR CAPITAL_PARIS" mapped-value="1"/>
            <qti-map-entry map-key="COUNTRY_DE CAPITAL_BERLIN" mapped-value="1"/>
            <qti-map-entry map-key="COUNTRY_ES CAPITAL_MADRID" mapped-value="1"/>
        </qti-mapping>
    </qti-response-declaration>

    <qti-outcome-declaration identifier="SCORE" cardinality="single" base-type="float"/>

    <qti-item-body>
        <qti-match-interaction response-identifier="RESPONSE"
            shuffle="true" max-associations="3">
            <qti-prompt>Match each country to its capital city.</qti-prompt>
            <qti-simple-match-set>
                <qti-simple-associable-choice identifier="COUNTRY_FR" match-max="1">
                    France
                </qti-simple-associable-choice>
                <qti-simple-associable-choice identifier="COUNTRY_DE" match-max="1">
                    Germany
                </qti-simple-associable-choice>
                <qti-simple-associable-choice identifier="COUNTRY_ES" match-max="1">
                    Spain
                </qti-simple-associable-choice>
            </qti-simple-match-set>
            <qti-simple-match-set>
                <qti-simple-associable-choice identifier="CAPITAL_PARIS" match-max="1">
                    Paris
                </qti-simple-associable-choice>
                <qti-simple-associable-choice identifier="CAPITAL_BERLIN" match-max="1">
                    Berlin
                </qti-simple-associable-choice>
                <qti-simple-associable-choice identifier="CAPITAL_MADRID" match-max="1">
                    Madrid
                </qti-simple-associable-choice>
            </qti-simple-match-set>
        </qti-match-interaction>
    </qti-item-body>

    <qti-response-processing>
        <qti-set-outcome-value identifier="SCORE">
            <qti-map-response identifier="RESPONSE"/>
        </qti-set-outcome-value>
    </qti-response-processing>
</qti-assessment-item>
```

**Validation Rules:**
- Minimum 2 items in each set
- Each source must have at least one valid target association
- `max-associations` ≥ number of required matches

---

### 5. Gap Match Interaction

**Description**: Learner drags text/images into gaps within a passage.

**Authoring UI Inputs:**
- Rich text content with gap markers (inserted via toolbar)
- Pool of draggable items (gap choices)
- Correct mapping of which item goes in which gap
- Distractor items (items that don't belong in any gap)
- `match-max` per gap choice

**Generated XML Structure:**
```xml
<qti-assessment-item identifier="gapmatch-q1" title="Drag and Drop">

    <qti-response-declaration identifier="RESPONSE"
        cardinality="multiple" base-type="directedPair">
        <qti-correct-response>
            <qti-value>WORD_SUN GAP_1</qti-value>
            <qti-value>WORD_ENERGY GAP_2</qti-value>
        </qti-correct-response>
        <qti-mapping default-value="0">
            <qti-map-entry map-key="WORD_SUN GAP_1" mapped-value="1"/>
            <qti-map-entry map-key="WORD_ENERGY GAP_2" mapped-value="1"/>
        </qti-mapping>
    </qti-response-declaration>

    <qti-outcome-declaration identifier="SCORE" cardinality="single" base-type="float"/>

    <qti-item-body>
        <qti-gap-match-interaction response-identifier="RESPONSE" shuffle="true">
            <qti-prompt>Drag the correct words into the gaps.</qti-prompt>

            <!-- Draggable items -->
            <qti-gap-text identifier="WORD_SUN" match-max="1">Sun</qti-gap-text>
            <qti-gap-text identifier="WORD_ENERGY" match-max="1">energy</qti-gap-text>
            <qti-gap-text identifier="WORD_MOON" match-max="1">Moon</qti-gap-text>

            <!-- Text with gaps -->
            <p>Plants use light from the <qti-gap identifier="GAP_1"/> to produce
               <qti-gap identifier="GAP_2"/> through photosynthesis.</p>
        </qti-gap-match-interaction>
    </qti-item-body>

    <qti-response-processing>
        <qti-set-outcome-value identifier="SCORE">
            <qti-map-response identifier="RESPONSE"/>
        </qti-set-outcome-value>
    </qti-response-processing>
</qti-assessment-item>
```

**TipTap Integration:**
Custom `GapNode` that renders as `[___]` placeholder in editor, with associated gap identifier.

---

## Frontend Architecture

### Design Decision: Intermediate JSON Format

After analyzing Studio's existing architecture, I will use an **intermediate JSON format** rather than direct XML editing. This decision is based on:

1. **Consistency**: Current `AssessmentItem` model stores `answers` and `hints` as JSON
2. **Simplicity**: JSON is easier to manipulate in Vue.js than XML DOM
3. **Validation**: Pydantic models on backend validate during JSON→XML conversion
4. **Existing Pattern**: `QTIExerciseGenerator` already converts internal format to QTI XML

### Component Architecture

```
AssessmentItemEditor (enhanced)
├── QuestionTypeSelector
│   └── [Extended with new types]
├── QuestionTextEditor (TipTapEditor)
│   └── [Extended with InlineChoice and Gap nodes]
│
├── [Type-specific editors - NEW]
│   ├── OrderInteractionEditor
│   │   ├── OrderableItemsList (drag-to-reorder)
│   │   └── OrderItemEditor (per item)
│   │
│   ├── MatchInteractionEditor
│   │   ├── MatchSetEditor (source column)
│   │   ├── MatchSetEditor (target column)
│   │   └── AssociationEditor (connections)
│   │
│   ├── InlineChoiceEditor
│   │   └── InlineChoiceDialog (edit choices for selected marker)
│   │
│   ├── GapMatchEditor
│   │   ├── GapChoicesPool (draggable items list)
│   │   └── GapMappingEditor
│   │
│   └── TextEntryEditor (enhanced)
│       ├── AcceptedAnswersList
│       └── PartialCreditMapper
│
└── HintsEditor (existing)
```

### State Management (Vuex)

Extend existing `assessmentItem` Vuex module:

```javascript
// vuex/assessmentItem/state.js
export default {
  // Existing
  assessmentItems: {},

  // New: type-specific data
  orderInteractionData: {},    // { [assessmentId]: { items: [], shuffle: bool } }
  matchInteractionData: {},    // { [assessmentId]: { sourceSet: [], targetSet: [], associations: [] } }
  inlineChoiceData: {},        // { [assessmentId]: { choices: { [responseId]: [] } } }
  gapMatchData: {},            // { [assessmentId]: { gapChoices: [], gaps: [], associations: [] } }
};
```

### TipTap Extensions for Inline Interactions

For Inline Choice and Gap Match, I'll create custom TipTap nodes:

```javascript
// InlineChoiceNode.js
import { Node } from '@tiptap/core';
import { VueNodeViewRenderer } from '@tiptap/vue-2';
import InlineChoiceNodeView from './InlineChoiceNodeView.vue';

export const InlineChoiceNode = Node.create({
  name: 'inlineChoice',
  group: 'inline',
  inline: true,
  atom: true,

  addAttributes() {
    return {
      responseIdentifier: { default: null },
      choices: { default: [] },
      correctChoice: { default: null },
      shuffle: { default: true },
    };
  },

  parseHTML() {
    return [{ tag: 'span[data-inline-choice]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', { 'data-inline-choice': '', ...HTMLAttributes }];
  },

  addNodeView() {
    return VueNodeViewRenderer(InlineChoiceNodeView);
  },
});
```

---

## Backend Architecture

### Database Schema

**Option Selected: Extend AssessmentItem with JSONField**

Rather than creating separate models per interaction type (which would complicate queries and migrations), I'll store type-specific data in a new JSON field:

```python
# models.py - Proposed changes
class AssessmentItem(models.Model):
    # Existing fields
    type = models.CharField(max_length=50, choices=ASSESSMENT_ITEM_TYPES)
    question = models.TextField(blank=True)
    hints = models.TextField(default="[]")
    answers = models.TextField(default="[]")  # Used for simple choice types
    order = models.IntegerField(default=0)
    contentnode = models.ForeignKey(ContentNode, related_name="assessment_items")
    assessment_id = UUIDField(default=uuid.uuid4)
    randomize = models.BooleanField(default=False)

    # NEW: Flexible storage for complex interaction data
    extra_data = models.JSONField(default=dict, blank=True)
    # Structure varies by type:
    # - order_interaction: {"items": [...], "shuffle": bool}
    # - match_interaction: {"source_set": [...], "target_set": [...], "associations": [...]}
    # - inline_choice: {"interactions": [{"response_id": "...", "choices": [...]}]}
    # - gap_match: {"gap_choices": [...], "gaps": [...], "associations": [...]}
```

**New Question Types:**
```python
# constants/exercises.py
SINGLE_SELECTION = "single_selection"
MULTIPLE_SELECTION = "multiple_selection"
INPUT_QUESTION = "input_question"
TRUE_FALSE = "true_false"
FREE_RESPONSE = "free_response"
PERSEUS_QUESTION = "perseus_question"

# NEW
ORDER_INTERACTION = "order_interaction"
MATCH_INTERACTION = "match_interaction"
INLINE_CHOICE = "inline_choice"
TEXT_ENTRY = "text_entry"  # Enhanced from input_question
GAP_MATCH = "gap_match"
```

### API Endpoints

The existing `/api/assessmentitem/` endpoint with bulk CRUD support will be extended:

```python
# viewsets/assessmentitem.py

class AssessmentItemViewSet(BulkModelViewSet):
    serializer_class = AssessmentItemSerializer

    # Existing: handles creation, updates, deletion
    # Changes needed:
    # 1. Update serializer to handle extra_data field
    # 2. Add validation based on type
```

**Serializer Enhancement:**
```python
# serializers/assessmentitem.py

class AssessmentItemSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    extra_data = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = AssessmentItem
        fields = ['id', 'type', 'question', 'answers', 'hints',
                  'order', 'randomize', 'extra_data', 'contentnode', 'assessment_id']

    def validate(self, data):
        item_type = data.get('type')
        extra_data = data.get('extra_data', {})

        # Type-specific validation
        if item_type == 'order_interaction':
            self._validate_order_interaction(extra_data)
        elif item_type == 'match_interaction':
            self._validate_match_interaction(extra_data)
        # ... etc

        return data

    def _validate_order_interaction(self, extra_data):
        items = extra_data.get('items', [])
        if len(items) < 2:
            raise serializers.ValidationError(
                "Order interaction requires at least 2 items"
            )
```

### XML Generation Logic

Extend `QTIExerciseGenerator` in `utils/assessment/qti/archive.py`:

```python
class QTIExerciseGenerator(ExerciseArchiveGenerator):

    def create_assessment_item(self, assessment_item, processed_data):
        item_type = assessment_item.type

        if item_type in ['single_selection', 'multiple_selection', 'true_false']:
            return self._create_choice_interaction(assessment_item, processed_data)
        elif item_type == 'order_interaction':
            return self._create_order_interaction(assessment_item, processed_data)
        elif item_type == 'match_interaction':
            return self._create_match_interaction(assessment_item, processed_data)
        elif item_type == 'inline_choice':
            return self._create_inline_choice_interaction(assessment_item, processed_data)
        elif item_type == 'gap_match':
            return self._create_gap_match_interaction(assessment_item, processed_data)
        elif item_type == 'text_entry':
            return self._create_text_entry_interaction(assessment_item, processed_data)

    def _create_order_interaction(self, assessment_item, processed_data):
        extra_data = assessment_item.extra_data
        items = extra_data.get('items', [])

        # Build response declaration
        response_decl = ResponseDeclaration(
            identifier="RESPONSE",
            cardinality=Cardinality.ORDERED,
            base_type=BaseType.IDENTIFIER,
            correct_response=CorrectResponse(
                values=[Value(value=item['identifier']) for item in sorted(items, key=lambda x: x['order'])]
            )
        )

        # Build interaction
        interaction = OrderInteraction(
            response_identifier="RESPONSE",
            shuffle=extra_data.get('shuffle', True),
            orientation=Orientation(extra_data.get('orientation', 'vertical')),
            prompt=Prompt(children=[...]),  # Parsed from question
            answers=[
                SimpleChoice(
                    identifier=item['identifier'],
                    children=self._parse_rich_content(item['content'])
                )
                for item in items
            ]
        )

        # Assemble complete item
        return AssessmentItem(
            identifier=str(assessment_item.assessment_id),
            title=self._generate_title(assessment_item),
            response_declaration=[response_decl],
            outcome_declaration=[self._default_outcome()],
            item_body=ItemBody(children=[interaction]),
            response_processing=ResponseProcessing(
                template=MATCH_CORRECT_TEMPLATE
            )
        )
```

### New Pydantic Models

```python
# utils/assessment/qti/interaction_types/order.py

class OrderInteraction(BlockInteraction):
    """QTI 3.0 Order Interaction"""
    shuffle: Optional[bool] = True
    min_choices: Optional[NonNegativeInt] = None
    max_choices: Optional[NonNegativeInt] = None
    orientation: Orientation = Orientation.VERTICAL
    prompt: Optional[Prompt] = None
    answers: Annotated[List[SimpleChoice], Len(min_length=2)]

    @model_validator(mode='after')
    def validate_choices(self):
        if self.min_choices and self.min_choices > len(self.answers):
            raise ValueError("min_choices cannot exceed number of answers")
        return self


# utils/assessment/qti/interaction_types/match.py

class SimpleAssociableChoice(QTIBase, BaseSequence):
    identifier: QTIIdentifier
    match_min: NonNegativeInt = 0
    match_max: PositiveInt = 1
    children: FlowContentList


class SimpleMatchSet(QTIBase):
    choices: Annotated[List[SimpleAssociableChoice], Len(min_length=1)]


class MatchInteraction(BlockInteraction):
    """QTI 3.0 Match Interaction"""
    shuffle: Optional[bool] = True
    max_associations: Optional[NonNegativeInt] = None
    min_associations: Optional[NonNegativeInt] = 0
    prompt: Optional[Prompt] = None
    source_set: SimpleMatchSet
    target_set: SimpleMatchSet
```

---

## Implementation Priority

Based on complexity, dependencies, and pattern reusability:

| Priority | Interaction Type | Weeks | Rationale |
|----------|------------------|-------|-----------|
| **1** | Order Interaction | 2 | Simplest new type; reuses existing `SimpleChoice`; establishes patterns |
| **2** | Text Entry (enhanced) | 1.5 | Builds on existing `input_question`; adds string support |
| **3** | Inline Choice | 2.5 | Medium complexity; introduces TipTap custom nodes |
| **4** | Match Interaction | 2.5 | New UI paradigm (two columns); introduces `directedPair` handling |
| **5** | Gap Match | 3 | Most complex; combines TipTap nodes + drag-drop + `directedPair` |

**Shared Patterns:**
- Order & Choice share `SimpleChoice` Pydantic model
- Match & Gap Match share `directedPair` response handling
- Inline Choice & Gap Match both need TipTap extension integration

---

## Testing Strategy

### 1. Unit Tests (Frontend - Jest)

```javascript
// OrderInteractionEditor.spec.js
describe('OrderInteractionEditor', () => {
  it('renders all items in the list', () => { /* ... */ });
  it('allows reordering via drag and drop', () => { /* ... */ });
  it('emits update event with new order', () => { /* ... */ });
  it('validates minimum 2 items required', () => { /* ... */ });
  it('generates unique identifiers for new items', () => { /* ... */ });
});

// validation.spec.js (extended)
describe('getAssessmentItemErrors', () => {
  describe('order_interaction', () => {
    it('returns error if fewer than 2 items', () => { /* ... */ });
    it('returns error if any item has empty content', () => { /* ... */ });
    it('passes validation for valid order interaction', () => { /* ... */ });
  });
});
```

### 2. Unit Tests (Backend - pytest)

```python
# test_qti_order_interaction.py
class TestOrderInteractionModel:
    def test_valid_order_interaction(self):
        """Test valid OrderInteraction Pydantic model"""
        interaction = OrderInteraction(
            response_identifier="RESPONSE",
            shuffle=True,
            answers=[
                SimpleChoice(identifier="A", children=[...]),
                SimpleChoice(identifier="B", children=[...]),
            ]
        )
        assert interaction.shuffle is True
        assert len(interaction.answers) == 2

    def test_minimum_answers_validation(self):
        """Test that OrderInteraction requires at least 2 answers"""
        with pytest.raises(ValidationError):
            OrderInteraction(
                response_identifier="RESPONSE",
                answers=[SimpleChoice(identifier="A", children=[...])]
            )


# test_qti_generation.py
class TestQTIGeneration:
    def test_order_interaction_xml_output(self, order_assessment_item):
        """Test complete XML generation for order interaction"""
        generator = QTIExerciseGenerator(content_node)
        xml = generator.create_assessment_item(order_assessment_item, {})

        root = ET.fromstring(xml.to_xml_string())

        # Verify structure
        assert root.tag == '{http://www.imsglobal.org/xsd/imsqtiasi_v3p0}qti-assessment-item'

        response_decl = root.find('.//{...}qti-response-declaration')
        assert response_decl.get('cardinality') == 'ordered'

        order_interaction = root.find('.//{...}qti-order-interaction')
        assert order_interaction is not None
        assert len(order_interaction.findall('.//{...}qti-simple-choice')) >= 2
```

### 3. Integration Tests

```python
# test_assessment_item_api.py
class TestAssessmentItemAPI:
    def test_create_order_interaction(self, api_client, content_node):
        """Test creating order interaction via API"""
        response = api_client.post('/api/assessmentitem/', {
            'type': 'order_interaction',
            'question': '<p>Order these steps</p>',
            'contentnode': str(content_node.id),
            'extra_data': {
                'items': [
                    {'identifier': 'STEP_1', 'content': 'First', 'order': 1},
                    {'identifier': 'STEP_2', 'content': 'Second', 'order': 2},
                ],
                'shuffle': True
            }
        })
        assert response.status_code == 201
        assert response.data['type'] == 'order_interaction'

    def test_export_qti_with_order_interaction(self, content_node_with_order_questions):
        """Test full QTI export includes order interactions correctly"""
        # Trigger export
        # Verify generated ZIP contains valid QTI XML
        # Validate against QTI 3.0 schema
```

### 4. Kolibri Viewer Compatibility Tests

```python
# test_kolibri_compatibility.py
class TestKolibriViewerCompatibility:
    """Tests that generated QTI works in Kolibri's QTI viewer plugin"""

    @pytest.fixture
    def kolibri_qti_viewer(self):
        # Setup Kolibri test environment with QTI viewer
        pass

    def test_order_interaction_renders(self, kolibri_qti_viewer, generated_qti):
        """Verify order interaction renders in Kolibri viewer"""
        # Load QTI in viewer
        # Verify interaction is functional
        # Test scoring works correctly

    def test_match_interaction_renders(self, kolibri_qti_viewer, generated_qti):
        """Verify match interaction renders in Kolibri viewer"""
        pass
```

### 5. E2E Tests (Cucumber/Gherkin)

```gherkin
# features/order_interaction.feature
Feature: Order Interaction Authoring
  As a content creator
  I want to create order/sequencing questions
  So that learners can demonstrate sequential understanding

  Scenario: Create a new order interaction question
    Given I am editing an exercise
    When I click "Add Question"
    And I select "Order/Sequence" as the question type
    And I enter "Arrange these historical events chronologically" as the question
    And I add the following items:
      | content                    |
      | World War I begins         |
      | World War II ends          |
      | Moon landing               |
    And I arrange them in correct order
    And I click "Save"
    Then the question should be saved successfully
    And I should see the question in the question list

  Scenario: Validate order interaction requires minimum items
    Given I am creating an order interaction question
    When I add only one item
    Then I should see an error "At least 2 items required"
```

---

## Risks and Challenges

### 1. Kolibri Viewer Compatibility

**Risk**: Generated QTI XML may not render correctly in Kolibri's QTI viewer plugin.

**Mitigation**:
- Study Kolibri's `kolibri-plugin-qti-viewer` source code early
- Create compatibility test suite that runs against actual viewer
- Maintain close communication with Kolibri core team
- Document any QTI features not supported by viewer

### 2. Complex Rich Text + Interactions

**Risk**: TipTap integration for inline choice and gap match may be complex.

**Mitigation**:
- Study existing TipTap extensions in Studio codebase
- Build proof-of-concept for custom nodes early (Week 1-2)
- Have fallback plan: simpler UI with placeholder markers if needed
- Reference other TipTap plugin examples (mentions, embeds)

### 3. Validation Complexity

**Risk**: Validating complex associations (match pairs, gap mappings) is error-prone.

**Mitigation**:
- Use Pydantic for strict backend validation
- Implement frontend validation that mirrors backend rules
- Comprehensive error messages for authors
- Unit tests for every validation rule

### 4. Performance with Many Choices

**Risk**: Match/order interactions with 20+ items could have performance issues.

**Mitigation**:
- Implement virtualized lists (vue-virtual-scroller) if needed
- Set reasonable maximum limits (configurable)
- Lazy loading for choice content

### 5. QTI Specification Complexity

**Risk**: QTI 3.0 spec has many optional features; unclear which to support.

**Mitigation**:
- Focus on core interaction attributes first
- Document unsupported features clearly
- Design extensible architecture for future additions

### 6. Version Updates

**Risk**: QTI spec or Kolibri viewer may update during/after project.

**Mitigation**:
- Abstract XML generation behind version-aware templates
- Use namespace constants rather than hardcoded strings
- Document version dependencies

---

## Timeline

**Program**: GSoC 2026 (assuming 12-week standard timeline)
**Commitment**: [FULL-TIME / PART-TIME - specify hours per week]

### Community Bonding Period (Weeks 0-1)
- Deep dive into Kolibri QTI viewer plugin source
- Set up comprehensive development environment
- Create detailed technical design document for review
- Build proof-of-concept for TipTap custom nodes
- Establish testing infrastructure

### Phase 1: Foundation (Weeks 2-4)

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 2 | Order Interaction - Backend | Pydantic model, XML generation, API updates |
| 3 | Order Interaction - Frontend | Vue component, Vuex integration, validation |
| 4 | Testing + Text Entry Enhancement | Unit tests, integration tests, string support for text entry |

**Milestone 1 Deliverables:**
- Working Order Interaction (full stack)
- Enhanced Text Entry with string support
- Test coverage >80% for new code

### Phase 2: Inline Interactions (Weeks 5-7)

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 5 | TipTap Custom Node Foundation | InlineChoiceNode, GapNode base implementations |
| 6 | Inline Choice - Full Implementation | Backend + frontend + tests |
| 7 | Match Interaction - Backend | Pydantic models, XML generation, directedPair handling |

**Milestone 2 Deliverables:**
- Working Inline Choice Interaction
- Match Interaction backend complete
- TipTap extension patterns documented

### Phase 3: Complex Interactions (Weeks 8-10)

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 8 | Match Interaction - Frontend | Two-column UI, association editor |
| 9 | Gap Match - Backend | Pydantic models, XML generation |
| 10 | Gap Match - Frontend | Drag-drop UI, gap markers in editor |

**Milestone 3 Deliverables:**
- Working Match Interaction
- Working Gap Match Interaction
- All interaction types functional

### Phase 4: Polish & Documentation (Weeks 11-12)

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 11 | Integration testing, bug fixes | E2E tests, Kolibri viewer compatibility verified |
| 12 | Documentation, code review, final polish | Architecture docs, contributor guide, PR ready |

**Final Deliverables:**
- All 5 interaction types production-ready
- Comprehensive test suite
- Documentation for future contributors
- Clean PR ready for merge

---

## About Me

### Personal Background
[Write 2-3 sentences about yourself, your interests, and motivation for this project]

### Technical Skills

| Category | Skills |
|----------|--------|
| **Languages** | Python, JavaScript/TypeScript, HTML/CSS |
| **Frontend** | Vue.js (2.x and 3.x), Vuex, TipTap/ProseMirror |
| **Backend** | Django, Django REST Framework, PostgreSQL |
| **Testing** | Jest, pytest, Cypress |
| **Tools** | Git, Docker, CI/CD |

### Relevant Experience

**[Project/Experience 1]**
- Brief description
- Technologies used
- Your role and contributions

**[Project/Experience 2]**
- Brief description
- Technologies used
- Your role and contributions

### Open Source Contributions

| Repository | Contribution | Link |
|------------|--------------|------|
| [repo-name] | [description] | [PR/issue link] |
| kolibri-studio | [your contribution if any] | [link] |

### Why This Project?

[Write 2-3 paragraphs explaining:
1. Why you're interested in educational technology / Kolibri's mission
2. Why this specific project excites you
3. What unique perspective or skills you bring]

### Availability

- **Weekly Hours**: [e.g., "35-40 hours/week (full-time)"]
- **Other Commitments**: [e.g., "University exams Week 5-6, reduced to 20 hours"]
- **Timezone**: [e.g., "UTC+5:30 (India)"]

---

## References

1. QTI 3.0 Specification - IMS Global: https://www.imsglobal.org/spec/qti/v3p0
2. QTI 3.0 Best Practices Guide: https://www.imsglobal.org/spec/qti/v3p0/guide
3. Kolibri Studio Repository: https://github.com/learningequality/studio
4. Kolibri QTI Viewer Plugin: https://github.com/learningequality/kolibri-plugin-qti-viewer
5. TipTap Editor Documentation: https://tiptap.dev/
6. Vue.js 2.x Documentation: https://v2.vuejs.org/
7. Pydantic Documentation: https://docs.pydantic.dev/

---

*This proposal was prepared for Google Summer of Code 2026 with Learning Equality.*
