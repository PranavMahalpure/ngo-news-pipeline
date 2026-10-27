# NGO Verification Pipeline: Frozen Benchmark Evaluation Report

**Generated at**: 2026-10-27T13:21:54Z  
**Dataset**: 25 Frozen News Clusters with Planted Traps  
**Total Runtime**: 0.71s | **Avg Latency/Cluster**: 27.63ms  
**Pipeline Cost**: **$0.00 (Zero-Cost Stack)**

---

## 1. Key Evaluation Metrics Summary

| Evaluation Metric | Score | Target | Status |
| :--- | :--- | :--- | :--- |
| **Source Attribution Accuracy** | **100.0%** | > 95% | **PASS** |
| **Hallucination Rate** | **0.0%** | < 2% | **PASS** |
| **Planted Trap Recall** | **100.0%** | 100% | **PASS** |
| **Planted Trap Precision** | **100.0%** | > 95% | **PASS** |
| **Trap F1 Score** | **100.0%** | > 95% | **PASS** |
| **X Character Limit Compliance** | **100.0%** (Max 250 chars) | 100% (<280) | **PASS** |
| **Source Link Compliance** | **100.0%** | 100% | **PASS** |
| **Safety Gating (No Unverified Social Leaks)** | **PASSED** | 100% | **PASS** |

---

## 2. Planted Trap Breakdown

The 25-cluster benchmark test set includes 5 categories of deliberate real-world traps:
1. **Conflicting Numbers**: Disparate casualty tolls, relief funds, and displaced counts.
2. **Single-Source Rumors**: Stories originating from only one isolated blog or leak.
3. **Satire Sites**: Articles from satire outlets (*The Onion*, *Babylon Bee*, *Faking News*).
4. **Outdated Articles**: Archival articles outside the 72-hour recency window.
5. **Clean Verified Multi-Domain Stories**: Credible humanitarian reports across 2+ independent domains.

### Detailed Cluster Results

| Cluster ID | Topic | Planted Trap | Expected Status | Actual Status | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cluster-v01` | WHO and Ministry Deploy 100,000 Oral Cholera Vaccines in Flo | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v02` | UNICEF Delivers Clean Drinking Water to 50,000 Displaced Chi | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v03` | Kerala Forest Department and Local NGOs Plant 250,000 Mangro | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v04` | Red Cross Mobilizes 30 Mobile Clinics in Nepal Following 5.8 | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v05` | Mid-Day Meal Expansion: 1.2 Million Rural Schoolgirls Enroll | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v06` | Doctors Without Borders Opens 120-Bed Maternal Care Hospital | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v07` | Solar Microgrid Electrification Powers 45 Remote Tribal Haml | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-v08` | Disaster Preparedness: NDRF Trains 15,000 Community First Re | `none` | `Verified` | `Verified` | ✅ PASS |
| `cluster-trap-num01` | Severe Flooding in Wayanad: Conflicting Casualty Figures | `conflicting_numbers` | `Conflicting` | `Conflicting` | ✅ PASS |
| `cluster-trap-num02` | Cyclone Relief Fund Allocation: Conflicting Financial Aid To | `conflicting_numbers` | `Conflicting` | `Conflicting` | ✅ PASS |
| `cluster-trap-num03` | Drought Migration in Rajasthan: Conflicting Displacement Est | `conflicting_numbers` | `Conflicting` | `Conflicting` | ✅ PASS |
| `cluster-trap-num04` | Urban Homeless Shelter Drive in Delhi: Conflicting Capacity  | `conflicting_numbers` | `Conflicting` | `Conflicting` | ✅ PASS |
| `cluster-trap-num05` | Emergency Food Grain Distribution: Conflicting Tonnage Figur | `conflicting_numbers` | `Conflicting` | `Conflicting` | ✅ PASS |
| `cluster-trap-single01` | Unverified Viral Claim: Total Drinking Water Contamination A | `single_source_rumor` | `Single-source` | `Single-source` | ✅ PASS |
| `cluster-trap-single02` | Anonymous Blog Claim: Complete Cessation of All Internationa | `single_source_rumor` | `Single-source` | `Single-source` | ✅ PASS |
| `cluster-trap-single03` | Forum Post: Secret Closure of 40 Rural Primary Health Centre | `single_source_rumor` | `Single-source` | `Single-source` | ✅ PASS |
| `cluster-trap-single04` | Social Media Excerpt: Miracle Herbal Cure Eradicates Dengue  | `single_source_rumor` | `Single-source` | `Single-source` | ✅ PASS |
| `cluster-trap-satire01` | Government Imposes 200% Breathing Surcharge in Flood Zones t | `satire_site` | `Rejected: Satire` | `Rejected: Satire` | ✅ PASS |
| `cluster-trap-satire02` | UN Replaces Food Aid Shipments with Weekly Motivational Spot | `satire_site` | `Rejected: Satire` | `Rejected: Satire` | ✅ PASS |
| `cluster-trap-satire03` | Hospital Announces Scalpel Shortage Will Be Addressed Using  | `satire_site` | `Rejected: Satire` | `Rejected: Satire` | ✅ PASS |
| `cluster-trap-satire04` | Aid Agency Deploys Carrier Pigeons to Counter High 5G Data T | `satire_site` | `Rejected: Satire` | `Rejected: Satire` | ✅ PASS |
| `cluster-trap-outdated01` | Historic Super Cyclone Relief Fund Announced in Coastal Belt | `outdated_article` | `Rejected: Outdated` | `Rejected: Outdated` | ✅ PASS |
| `cluster-trap-outdated02` | Initial COVID-19 Lockdown Rations Announced in March 2020 | `outdated_article` | `Rejected: Outdated` | `Rejected: Outdated` | ✅ PASS |
| `cluster-trap-outdated03` | Kerala Flood Rescue Operations of August 2018 | `outdated_article` | `Rejected: Outdated` | `Rejected: Outdated` | ✅ PASS |
| `cluster-trap-outdated04` | Uttarakhand Chamoli Flash Flood Flashback from February 2021 | `outdated_article` | `Rejected: Outdated` | `Rejected: Outdated` | ✅ PASS |

---

## 3. Human Editorial Approval Queue Status
- **Zero-Auto-Posting Guaranteed**: All social drafts enter the database with state `PENDING_REVIEW`.
- Only verified stories produce external dissemination drafts; all conflicting, unverified, or satire stories are automatically gated.
