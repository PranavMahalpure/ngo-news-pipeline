"""Frozen Evaluation Benchmark Test Set (25 News Clusters with Planted Traps).

Contains 25 reproducible, frozen snapshot clusters spanning humanitarian relief,
public health, education, and disaster response. Includes 5 distinct planted traps:
1. Conflicting numbers (disparate casualty and fund numbers)
2. Single-source rumors (unverified single domain leaks)
3. Satire sites (The Onion, Babylon Bee, Faking News)
4. Outdated articles (>72 hours old)
5. Clean verified multi-domain stories
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List
from ngo_pipeline.config import DEFAULT_CONFIG
from ngo_pipeline.models import (
    Article,
    EvaluationCluster,
    PlantedTrapType,
    VerificationStatus,
)

def build_frozen_benchmark() -> List[EvaluationCluster]:
    """Construct 25 deterministic evaluation clusters with planted traps and ground truths."""
    clusters: List[EvaluationCluster] = []

    # =========================================================================
    # Group 1: Clean Verified Multi-Domain Stories (Clusters 1 to 8)
    # =========================================================================
    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v01",
            topic="WHO and Ministry Deploy 100,000 Oral Cholera Vaccines in Flood-Hit Assam",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "100,000 oral cholera vaccines deployed to Assam flood zones.",
                "Coordinated between WHO and Ministry of Health.",
            ],
            articles=[
                Article(
                    url="https://thehindu.com/news/national/assam-cholera-drive-2026",
                    domain="thehindu.com",
                    title="Assam receives 100,000 oral cholera vaccines following monsoon floods",
                    raw_text="The Ministry of Health in collaboration with WHO officials has dispatched 100,000 oral cholera vaccines to flood-affected districts in Assam. Emergency medical camps have been established in 6 districts to prevent waterborne disease outbreaks.",
                    published_at="2026-10-26T10:00:00Z",
                    age_hours=24.0,
                ),
                Article(
                    url="https://bbc.com/news/world-asia-india-assam-health",
                    domain="bbc.com",
                    title="WHO and Indian authorities deploy 100,000 cholera doses in Assam",
                    raw_text="Health authorities in Assam have initiated an emergency inoculation campaign with 100,000 cholera vaccines provided through WHO coordination. Flooding in the Brahmaputra valley displaced thousands, prompting urgent preventive health steps.",
                    published_at="2026-10-26T11:30:00Z",
                    age_hours=22.5,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v02",
            topic="UNICEF Delivers Clean Drinking Water to 50,000 Displaced Children in Gaza",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "UNICEF delivered potable water to 50,000 children.",
                "Mobile desalination and water trucking operational.",
            ],
            articles=[
                Article(
                    url="https://reuters.com/world/middle-east/unicef-water-convoy-gaza",
                    domain="reuters.com",
                    title="UNICEF delivers clean water to 50,000 children in emergency convoy",
                    raw_text="UNICEF announced on Monday that emergency water distribution convoys reached southern regions, supplying clean potable water to over 50,000 displaced children through mobile desalination stations and purification tablets.",
                    published_at="2026-10-26T14:00:00Z",
                    age_hours=20.0,
                ),
                Article(
                    url="https://aljazeera.com/news/unicef-drinking-water-emergency",
                    domain="aljazeera.com",
                    title="Drinking water secured for 50,000 children via UNICEF aid drive",
                    raw_text="A coordinated humanitarian corridor enabled UNICEF to deliver safe drinking water for 50,000 vulnerable children today. Aid workers deployed water trucking to shelter centres across designated safety zones.",
                    published_at="2026-10-26T15:15:00Z",
                    age_hours=18.75,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v03",
            topic="Kerala Forest Department and Local NGOs Plant 250,000 Mangrove Saplings",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "250,000 mangrove saplings planted along coastal Kerala.",
                "Joint initiative between Kerala Forest Department and conservation NGOs.",
            ],
            articles=[
                Article(
                    url="https://thehindu.com/sci-tech/energy-and-environment/kerala-mangrove-drive",
                    domain="thehindu.com",
                    title="Kerala coastal resilience bolstered with 250,000 mangrove saplings",
                    raw_text="The Kerala Forest Department along with local wetland conservation NGOs completed planting 250,000 mangrove saplings along the Vembanad estuary. The initiative aims to form natural sea surge buffers for coastal fishing communities.",
                    published_at="2026-10-25T09:00:00Z",
                    age_hours=48.0,
                ),
                Article(
                    url="https://indianexpress.com/article/cities/thiruvananthapuram/mangrove-initiative",
                    domain="indianexpress.com",
                    title="Community drive plants 250,000 mangroves in Kerala coastal wetlands",
                    raw_text="Over three weekends, volunteers and Kerala Forest Department personnel successfully planted 250,000 mangrove saplings across coastal wetlands to restore degraded intertidal ecosystems.",
                    published_at="2026-10-25T12:00:00Z",
                    age_hours=45.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v04",
            topic="Red Cross Mobilizes 30 Mobile Clinics in Nepal Following 5.8 Magnitude Earthquake",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "Red Cross deployed 30 mobile health clinics in Nepal.",
                "Response triggered by 5.8 magnitude tremor in western districts.",
            ],
            articles=[
                Article(
                    url="https://kathmandupost.com/national/earthquake-relief-red-cross",
                    domain="kathmandupost.com",
                    title="Red Cross deploys 30 mobile health clinics across quake-hit districts",
                    raw_text="Following Sunday's 5.8 magnitude earthquake in western Nepal, Nepal Red Cross Society teams deployed 30 mobile clinics to treat trauma and deliver emergency primary medical care in remote hilly settlements.",
                    published_at="2026-10-26T08:00:00Z",
                    age_hours=26.0,
                ),
                Article(
                    url="https://reuters.com/world/asia-pacific/nepal-quake-emergency-aid",
                    domain="reuters.com",
                    title="International Red Cross dispatches 30 mobile clinics to western Nepal",
                    raw_text="Humanitarian responders confirmed 30 mobile clinic units were deployed to western Nepal after a 5.8 magnitude earthquake damaged access roads and village clinics.",
                    published_at="2026-10-26T09:30:00Z",
                    age_hours=24.5,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v05",
            topic="Mid-Day Meal Expansion: 1.2 Million Rural Schoolgirls Enrolled in Nutrition Programme",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "1.2 million rural schoolgirls enrolled in fortified nutrition scheme.",
                "Joint initiative between Education Ministry and Akshaya Patra Foundation.",
            ],
            articles=[
                Article(
                    url="https://pib.gov.in/PressReleasePage.aspx?PRID=1987654",
                    domain="pib.gov.in",
                    title="PM-POSHAN scheme expanded to cover 1.2 million additional girl students",
                    raw_text="The Ministry of Education announced an expansion of fortified midday meals reaching 1.2 million schoolgirls in aspirational rural districts to combat childhood anemia.",
                    published_at="2026-10-25T16:00:00Z",
                    age_hours=41.0,
                ),
                Article(
                    url="https://timesofindia.indiatimes.com/india/nutrition-drive-schools",
                    domain="timesofindia.indiatimes.com",
                    title="1.2 million schoolgirls covered under upgraded fortified nutrition rollout",
                    raw_text="State education departments in tandem with midday meal partners commenced hot meal distributions for 1.2 million girl students across 4,500 government primary schools.",
                    published_at="2026-10-25T18:00:00Z",
                    age_hours=39.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v06",
            topic="Doctors Without Borders Opens 120-Bed Maternal Care Hospital in Rural Chad",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "MSF opened a 120-bed maternal care hospital in Chad.",
                "Facility provides free emergency obstetrics and newborn intensive care.",
            ],
            articles=[
                Article(
                    url="https://msf.org/chad-maternal-health-hospital-opening",
                    domain="msf.org",
                    title="MSF inaugurates 120-bed specialized maternal health center in Chad",
                    raw_text="Doctors Without Borders (MSF) has officially opened a newly constructed 120-bed maternal and pediatric health facility in eastern Chad to reduce maternal mortality rates.",
                    published_at="2026-10-26T07:00:00Z",
                    age_hours=27.0,
                ),
                Article(
                    url="https://france24.com/en/africa/chad-msf-hospital-maternal-care",
                    domain="france24.com",
                    title="Chad: New 120-bed hospital launched by MSF for maternal and child health",
                    raw_text="The humanitarian organization Doctors Without Borders launched a 120-bed maternal hospital in Chad, providing emergency obstetric interventions for underserved communities.",
                    published_at="2026-10-26T09:00:00Z",
                    age_hours=25.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v07",
            topic="Solar Microgrid Electrification Powers 45 Remote Tribal Hamlets in Odisha",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "45 remote tribal hamlets electrified using decentralised solar microgrids.",
                "Project implemented by SELCO Foundation and Odisha Renewable Energy Development Agency.",
            ],
            articles=[
                Article(
                    url="https://downtoearth.org.in/energy/odisha-tribal-solar-microgrids",
                    domain="downtoearth.org.in",
                    title="45 remote tribal settlements in Odisha achieve round-the-clock solar power",
                    raw_text="The installation of off-grid solar microgrids has successfully energized 45 remote tribal hamlets in Koraput and Rayagada districts, powering community health centres and household lighting.",
                    published_at="2026-10-25T11:00:00Z",
                    age_hours=46.0,
                ),
                Article(
                    url="https://thehindu.com/news/national/other-states/odisha-solar-hamlets",
                    domain="thehindu.com",
                    title="Solar microgrids bring clean energy to 45 tribal villages in southern Odisha",
                    raw_text="A renewable energy collaborative project has commissioned standalone solar microgrids across 45 tribal hamlets, benefiting over 3,200 indigenous households.",
                    published_at="2026-10-25T13:30:00Z",
                    age_hours=43.5,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-v08",
            topic="Disaster Preparedness: NDRF Trains 15,000 Community First Responders in Coastal Odisha",
            planted_trap=PlantedTrapType.NONE,
            expected_status=VerificationStatus.VERIFIED,
            ground_truth_claims=[
                "15,000 coastal community volunteers trained in flood search and rescue.",
                "NDRF 3rd Battalion conducted drills across 12 vulnerable districts.",
            ],
            articles=[
                Article(
                    url="https://pib.gov.in/PressReleasePage.aspx?PRID=1991234",
                    domain="pib.gov.in",
                    title="NDRF completes disaster preparedness training for 15,000 community volunteers",
                    raw_text="The National Disaster Response Force (NDRF) concluded its coastal resilience curriculum, certifying 15,000 local youth and fishermen in early warning dissemination and first aid.",
                    published_at="2026-10-26T12:00:00Z",
                    age_hours=22.0,
                ),
                Article(
                    url="https://tribuneindia.com/news/nation/ndrf-coastal-volunteers",
                    domain="tribuneindia.com",
                    title="15,000 village first responders trained by NDRF ahead of cyclone season",
                    raw_text="In an intensive month-long initiative, NDRF battalions trained 15,000 coastal community volunteers in rapid boat rescue, shelter management, and triage operations.",
                    published_at="2026-10-26T14:30:00Z",
                    age_hours=19.5,
                ),
            ],
        )
    )

    # =========================================================================
    # Group 2: Planted Trap - Conflicting Numbers (Clusters 9 to 13)
    # =========================================================================
    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-num01",
            topic="Severe Flooding in Wayanad: Conflicting Casualty Figures",
            planted_trap=PlantedTrapType.CONFLICTING_NUMBERS,
            expected_status=VerificationStatus.CONFLICTING,
            expected_conflict_details="Discrepant counts: thehindu.com reports 42 dead, while bbc.com reports 118 dead.",
            articles=[
                Article(
                    url="https://thehindu.com/news/national/kerala/wayanad-floods-toll",
                    domain="thehindu.com",
                    title="Wayanad cloudburst: District collector confirms 42 dead as search intensifies",
                    raw_text="District administration officials in Wayanad confirmed that 42 people have died following landslides triggered by unprecedented rainfall. Rescue teams continue searching debris.",
                    published_at="2026-10-26T13:00:00Z",
                    age_hours=21.0,
                ),
                Article(
                    url="https://bbc.com/news/world-asia-india-wayanad-disaster",
                    domain="bbc.com",
                    title="Kerala landslide: Rescuers report 118 dead in northern hills",
                    raw_text="Local disaster management coordinators and hospital authorities report at least 118 dead after twin landslides swept through plantation villages in Wayanad during early morning hours.",
                    published_at="2026-10-26T14:00:00Z",
                    age_hours=20.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-num02",
            topic="Cyclone Relief Fund Allocation: Conflicting Financial Aid Totals",
            planted_trap=PlantedTrapType.CONFLICTING_NUMBERS,
            expected_status=VerificationStatus.CONFLICTING,
            expected_conflict_details="Discrepant fund figures: pib.gov.in reports 500 crore rupees, whereas telegraphindia.com reports 2500 crore rupees.",
            articles=[
                Article(
                    url="https://pib.gov.in/PressReleasePage.aspx?PRID=1998877",
                    domain="pib.gov.in",
                    title="Union Government approves 500 crore advance relief for cyclone rebuilding",
                    raw_text="The high-level inter-ministerial committee has sanctioned an immediate advance of 500 crore rupees from the National Disaster Response Fund for immediate restoration of power grids.",
                    published_at="2026-10-26T10:00:00Z",
                    age_hours=24.0,
                ),
                Article(
                    url="https://telegraphindia.com/india/cyclone-relief-package-centre",
                    domain="telegraphindia.com",
                    title="Centre sanctions 2500 crore mega rehabilitation package for coastal districts",
                    raw_text="Announcing comprehensive coastal assistance, central officials stated that 2500 crore rupees has been released to state treasuries for embankment reconstruction and shelter building.",
                    published_at="2026-10-26T11:00:00Z",
                    age_hours=23.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-num03",
            topic="Drought Migration in Rajasthan: Conflicting Displacement Estimates",
            planted_trap=PlantedTrapType.CONFLICTING_NUMBERS,
            expected_status=VerificationStatus.CONFLICTING,
            expected_conflict_details="Discrepant displacement counts: downtoearth.org.in reports 5,000 displaced, while hindustantimes.com reports 45,000 displaced.",
            articles=[
                Article(
                    url="https://downtoearth.org.in/water/rajasthan-drought-migration",
                    domain="downtoearth.org.in",
                    title="Groundwater depletion forces 5,000 pastoral families to migrate in western desert",
                    raw_text="Field monitoring reports show that approximately 5,000 displaced pastoral families have moved cattle towards the Indira Gandhi Canal due to dried village watering ponds.",
                    published_at="2026-10-25T14:00:00Z",
                    age_hours=43.0,
                ),
                Article(
                    url="https://hindustantimes.com/india-news/rajasthan-heatwave-exodus",
                    domain="hindustantimes.com",
                    title="Severe drought triggers mass displacement of 45,000 pastoralists in Barmer",
                    raw_text="Civil society groups estimate that at least 45,000 displaced individuals have left rural Barmer and Jaisalmer over the past fortnight seeking emergency fodder and tanker water.",
                    published_at="2026-10-25T16:30:00Z",
                    age_hours=40.5,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-num04",
            topic="Urban Homeless Shelter Drive in Delhi: Conflicting Capacity Statistics",
            planted_trap=PlantedTrapType.CONFLICTING_NUMBERS,
            expected_status=VerificationStatus.CONFLICTING,
            expected_conflict_details="Discrepant shelter numbers: 1,200 beds vs 8,500 beds.",
            articles=[
                Article(
                    url="https://thehindu.com/news/cities/Delhi/night-shelter-expansion",
                    domain="thehindu.com",
                    title="Delhi Government activates 1,200 winter shelter beds across transit hubs",
                    raw_text="The Delhi Urban Shelter Improvement Board announced today that 1,200 beds equipped with waterproof bedding and clean drinking water are now functional for homeless individuals.",
                    published_at="2026-10-26T06:00:00Z",
                    age_hours=28.0,
                ),
                Article(
                    url="https://timesofindia.indiatimes.com/city/delhi/homeless-winter-drive",
                    domain="timesofindia.indiatimes.com",
                    title="Over 8,500 night shelter beds readied as cold wave conditions approach",
                    raw_text="Authorities stated that emergency portacabins and permanent shelter homes now offer 8,500 beds with round-the-clock doctor availability across the National Capital Region.",
                    published_at="2026-10-26T08:00:00Z",
                    age_hours=26.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-num05",
            topic="Emergency Food Grain Distribution: Conflicting Tonnage Figures",
            planted_trap=PlantedTrapType.CONFLICTING_NUMBERS,
            expected_status=VerificationStatus.CONFLICTING,
            expected_conflict_details="Discrepant grain metrics: 15,000 tonnes vs 90,000 tonnes.",
            articles=[
                Article(
                    url="https://indianexpress.com/article/india/food-relief-bihar",
                    domain="indianexpress.com",
                    title="FCI releases 15,000 tonnes of subsidized wheat for northern flood pockets",
                    raw_text="Food Corporation of India godowns dispatched 15,000 tonnes of grain to state relief camps to ensure uninterrupted community kitchen operations.",
                    published_at="2026-10-26T09:00:00Z",
                    age_hours=25.0,
                ),
                Article(
                    url="https://tribuneindia.com/news/nation/grain-aid-bihar",
                    domain="tribuneindia.com",
                    title="State disaster authority mobilizes 90,000 tonnes of emergency grain reserves",
                    raw_text="Disaster relief warehouses announced a major mobilization of 90,000 tonnes of wheat and rice across 8 flood-isolated sub-divisions.",
                    published_at="2026-10-26T10:30:00Z",
                    age_hours=23.5,
                ),
            ],
        )
    )

    # =========================================================================
    # Group 3: Planted Trap - Single-Source Rumors (Clusters 14 to 17)
    # =========================================================================
    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-single01",
            topic="Unverified Viral Claim: Total Drinking Water Contamination Across Metro Area",
            planted_trap=PlantedTrapType.SINGLE_SOURCE_RUMOR,
            expected_status=VerificationStatus.SINGLE_SOURCE,
            articles=[
                Article(
                    url="https://unverified-buzz-blog.in/breaking-city-water-leak",
                    domain="unverified-buzz-blog.in",
                    title="Secret memo claims entire metropolitan municipal water supply infected with neurotoxin",
                    raw_text="An anonymous whistleblower posted a leaked memo asserting that municipal chlorination plants failed completely yesterday, contaminating water for 8 million city residents. No official agency has verified the claim.",
                    published_at="2026-10-26T15:00:00Z",
                    age_hours=19.0,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-single02",
            topic="Anonymous Blog Claim: Complete Cessation of All International Aid Flights",
            planted_trap=PlantedTrapType.SINGLE_SOURCE_RUMOR,
            expected_status=VerificationStatus.SINGLE_SOURCE,
            articles=[
                Article(
                    url="https://dark-corridors-insider.net/aid-flights-grounded",
                    domain="dark-corridors-insider.net",
                    title="All UN cargo and medical relief aircraft grounded worldwide by emergency order",
                    raw_text="A single uncorroborated post on a fringe aviation blog claims global civil aviation authorities halted all humanitarian air missions due to radar malfunctions.",
                    published_at="2026-10-26T12:00:00Z",
                    age_hours=22.0,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-single03",
            topic="Forum Post: Secret Closure of 40 Rural Primary Health Centres",
            planted_trap=PlantedTrapType.SINGLE_SOURCE_RUMOR,
            expected_status=VerificationStatus.SINGLE_SOURCE,
            articles=[
                Article(
                    url="https://state-whispers-forum.org/threads/phc-closure-memo",
                    domain="state-whispers-forum.org",
                    title="Leaked circular alleges 40 Primary Health Centres slated for immediate permanent shutdown",
                    raw_text="A message board user uploaded a photocopy claiming the district medical board will shutter 40 health centres this Friday without public notification.",
                    published_at="2026-10-26T11:00:00Z",
                    age_hours=23.0,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-single04",
            topic="Social Media Excerpt: Miracle Herbal Cure Eradicates Dengue in 24 Hours",
            planted_trap=PlantedTrapType.SINGLE_SOURCE_RUMOR,
            expected_status=VerificationStatus.SINGLE_SOURCE,
            articles=[
                Article(
                    url="https://holistic-cures-express.info/dengue-cure-breakthrough",
                    domain="holistic-cures-express.info",
                    title="Rare forest extract achieves 100% cure for dengue fever overnight",
                    raw_text="A standalone promotional webpage alleges an untested botanical concoction eliminates dengue virus within 24 hours. The claim lacks clinical trials and regulatory authorization.",
                    published_at="2026-10-26T14:00:00Z",
                    age_hours=20.0,
                )
            ],
        )
    )

    # =========================================================================
    # Group 4: Planted Trap - Satire Sites (Clusters 18 to 21)
    # =========================================================================
    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-satire01",
            topic="Government Imposes 200% Breathing Surcharge in Flood Zones to Offset Rescue Costs",
            planted_trap=PlantedTrapType.SATIRE_SITE,
            expected_status=VerificationStatus.REJECTED_SATIRE,
            articles=[
                Article(
                    url="https://theonion.com/govt-imposes-breathing-tax-flood-zones",
                    domain="theonion.com",
                    title="Budget Ministry Announces 200% Surcharge on Inhaling Oxygen in Natural Disaster Zones",
                    raw_text="In an innovative fiscal stabilization manoeuvre, treasury spokespersons announced that flood survivors who breathe compressed rescue air will be billed on a per-lungful basis.",
                    published_at="2026-10-26T10:00:00Z",
                    age_hours=24.0,
                    is_satire=True,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-satire02",
            topic="UN Replaces Food Aid Shipments with Weekly Motivational Spotify Podcasts",
            planted_trap=PlantedTrapType.SATIRE_SITE,
            expected_status=VerificationStatus.REJECTED_SATIRE,
            articles=[
                Article(
                    url="https://babylonbee.com/news/un-replaces-grain-convoys-with-podcasts",
                    domain="babylonbee.com",
                    title="UN Announces Groundbreaking Pivot from Sending Wheat to Sending Mindset Audiobooks",
                    raw_text="Humanitarian officials unveiled a lean aid paradigm where famine-struck populations will receive complimentary wireless earbuds streaming tips on positive financial manifestations.",
                    published_at="2026-10-26T08:00:00Z",
                    age_hours=26.0,
                    is_satire=True,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-satire03",
            topic="Hospital Announces Scalpel Shortage Will Be Addressed Using Butter Knives",
            planted_trap=PlantedTrapType.SATIRE_SITE,
            expected_status=VerificationStatus.REJECTED_SATIRE,
            articles=[
                Article(
                    url="https://fakingnews.com/health/butter-knives-in-surgery",
                    domain="fakingnews.com",
                    title="Department of Health Approves Silverware Cutlery for High-Risk Emergency Surgery",
                    raw_text="Following an administrative inventory delay, state surgeons have been instructed to spread antiseptic using serrated breakfast butter knives.",
                    published_at="2026-10-26T09:00:00Z",
                    age_hours=25.0,
                    is_satire=True,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-satire04",
            topic="Aid Agency Deploys Carrier Pigeons to Counter High 5G Data Tariffs",
            planted_trap=PlantedTrapType.SATIRE_SITE,
            expected_status=VerificationStatus.REJECTED_SATIRE,
            articles=[
                Article(
                    url="https://clickhole.com/ngo-reverts-to-trained-pigeons-for-field-dispatch",
                    domain="clickhole.com",
                    title="Logistics Agency Phase Out Satellite Radios in Favor of Enthusiastic Doves",
                    raw_text="An NGO communications team concluded that feeding breadcrumbs to carrier birds is substantially more cost-effective than international roaming packages.",
                    published_at="2026-10-26T12:00:00Z",
                    age_hours=22.0,
                    is_satire=True,
                )
            ],
        )
    )

    # =========================================================================
    # Group 5: Planted Trap - Outdated Articles (Clusters 22 to 25)
    # =========================================================================
    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-outdated01",
            topic="Historic Super Cyclone Relief Fund Announced in Coastal Belt",
            planted_trap=PlantedTrapType.OUTDATED_ARTICLE,
            expected_status=VerificationStatus.REJECTED_OUTDATED,
            articles=[
                Article(
                    url="https://thehindu.com/news/national/archive-cyclone-fani-relief-2019",
                    domain="thehindu.com",
                    title="Cabinet clears emergency relief following Cyclone Fani landfall in Puri",
                    raw_text="The Union Cabinet cleared immediate financial assistance following massive damage caused by Cyclone Fani across coastal Odisha districts in May 2019.",
                    published_at="2019-05-04T12:00:00Z",
                    age_hours=65000.0,
                ),
                Article(
                    url="https://reuters.com/article/world/cyclone-fani-devastation-odisha-2019",
                    domain="reuters.com",
                    title="Relief operations launched in eastern India after Cyclone Fani",
                    raw_text="Disaster management teams have commenced restoration of telecommunication towers following Cyclone Fani in May 2019.",
                    published_at="2019-05-05T08:00:00Z",
                    age_hours=64980.0,
                ),
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-outdated02",
            topic="Initial COVID-19 Lockdown Rations Announced in March 2020",
            planted_trap=PlantedTrapType.OUTDATED_ARTICLE,
            expected_status=VerificationStatus.REJECTED_OUTDATED,
            articles=[
                Article(
                    url="https://pib.gov.in/PressReleasePage.aspx?PRID=1608765",
                    domain="pib.gov.in",
                    title="PM Garib Kalyan Package: 1.70 Lakh Crore relief announced during nationwide lockdown",
                    raw_text="Finance Minister Smt. Nirmala Sitharaman announced an economic relief package to assist migrant workers during the 21-day COVID-19 lockdown in March 2020.",
                    published_at="2020-03-26T14:00:00Z",
                    age_hours=57000.0,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-outdated03",
            topic="Kerala Flood Rescue Operations of August 2018",
            planted_trap=PlantedTrapType.OUTDATED_ARTICLE,
            expected_status=VerificationStatus.REJECTED_OUTDATED,
            articles=[
                Article(
                    url="https://bbc.com/news/world-asia-india-kerala-floods-2018",
                    domain="bbc.com",
                    title="Kerala floods: Military mobilizes airlifts as dams open across 14 districts",
                    raw_text="The Indian Navy and Air Force launched Operation Madad to evacuate inundated villages across Kerala during the historic monsoon flooding of August 2018.",
                    published_at="2018-08-16T10:00:00Z",
                    age_hours=71000.0,
                )
            ],
        )
    )

    clusters.append(
        EvaluationCluster(
            cluster_id="cluster-trap-outdated04",
            topic="Uttarakhand Chamoli Flash Flood Flashback from February 2021",
            planted_trap=PlantedTrapType.OUTDATED_ARTICLE,
            expected_status=VerificationStatus.REJECTED_OUTDATED,
            articles=[
                Article(
                    url="https://indianexpress.com/article/india/glacier-burst-uttarakhand-chamoli-2021",
                    domain="indianexpress.com",
                    title="Glacial breach triggers flash flood in Rishi Ganga river basin",
                    raw_text="Rescue personnel from ITBP and NDRF rescued workers trapped in the Tapovan hydel tunnel after a glacial surge in February 2021.",
                    published_at="2021-02-07T11:00:00Z",
                    age_hours=49000.0,
                )
            ],
        )
    )

    return clusters

def save_benchmark_fixtures(filepath: Optional[Path] = None) -> Path:
    """Serialize the frozen benchmark dataset to JSON for durable, reproducible testing."""
    target_path = filepath or DEFAULT_CONFIG.frozen_dataset_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    clusters = build_frozen_benchmark()
    data = [c.model_dump() for c in clusters]
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return target_path

def load_frozen_benchmark(filepath: Optional[Path] = None) -> List[EvaluationCluster]:
    """Load benchmark dataset from disk, auto-generating if not yet written."""
    target_path = filepath or DEFAULT_CONFIG.frozen_dataset_path
    if not target_path.exists():
        save_benchmark_fixtures(target_path)
    with open(target_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    return [EvaluationCluster.model_validate(item) for item in raw_data]
