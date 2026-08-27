# INVEST Narrative Guard

Runs immediately after extracting `System.Description`. Verifies the HU expresses real business value, not just a functional requirement.

## Detection Algorithm

Search for three narrative components (case-insensitive):

| Component | Signals |
|-----------|---------|
| **Role** (As a) | `Como `, `As a `, `As an `, `En mi rol de`, `Siendo ` |
| **Action** (I want) | `quiero `, `necesito `, `deseo `, `I want `, `I need `, `me gustaría ` |
| **Benefit** (So that) | `para `, `para que `, `con el fin de `, `a fin de `, `so that `, `in order to `, `con el objetivo de ` |

## Outcomes

### All 3 present → Complete narrative ✅
Confidence: High. Continue without interruption.

### Missing only Benefit (So that) → Business value absent ⚠️
**Stops the flow.** Show user:
> **⚠️ Value Guard:** Description has Role and Action but **no benefit** (*"para que..."*).
> Without benefit, this HU doesn't communicate business value — it's a functional requirement in disguise.

Offer:
- **[B]** Enter benefit now — append to description before publishing
- **[F]** Publish without benefit (Medium confidence — recorded in local stamp)
- **[N]** Cancel and fix the file first

If user chooses **[B]**, request benefit text, concatenate to narrative with `**Para que:** ` prefix, update `System.Description`.

### Missing Role or Action → No structured narrative ⚠️
Doesn't block (may be a technical HU without explicit narrative), but confidence: Medium. Add warning in preview:
> `⚠️ Narrative: No Como/Quiero/Para structure detected. Verify description expresses business value.`

### Empty or unrecoverable description → ❌ Blocking
Same as description extraction failure — ask user before continuing.
