"""
Creates keywords.json for all 48 subtopics across the 12 clusters.

Run from the benchmark root (the folder containing cluster_config.json).
Idempotent — safe to re-run; will overwrite existing keywords.json files.
"""

import json
from pathlib import Path

# ---------- KEYWORDS DATA (one entry per subtopic_id) ----------
KEYWORDS = {
    # ===== c1: Middle East Flashpoint 2019-2020 =====
    "c1_a_us_iran": {
        "canonical_keywords": ["Assassination of Qasem Soleimani", "US-Iran tensions", "killing of Soleimani"],
        "entity_keywords": [
            "Qasem Soleimani", "Donald Trump", "Ayatollah Ali Khamenei", "Mike Pompeo",
            "Mark Esper", "Islamic Revolutionary Guard Corps", "Quds Force",
            "Baghdad International Airport", "Abu Mahdi al-Muhandis", "Kata'ib Hezbollah",
            "Ain al-Asad Air Base", "Hassan Rouhani", "Mohammad Javad Zarif"
        ],
        "event_keywords": [
            "Soleimani drone strike January 3 2020", "US embassy Baghdad attack",
            "Iranian missile strike on Ain al-Asad", "Ukraine International Airlines Flight 752 shootdown",
            "tanker attacks Gulf of Oman", "downing of US RQ-4 Global Hawk",
            "Aramco facilities attack September 2019"
        ],
        "broader_context": [
            "Joint Comprehensive Plan of Action withdrawal",
            "maximum pressure campaign", "Iraqi parliament US troop withdrawal vote",
            "uranium enrichment escalation"
        ],
    },
    "c1_b_syria": {
        "canonical_keywords": ["Syrian civil war", "Syrian conflict"],
        "entity_keywords": [
            "Bashar al-Assad", "Syrian Democratic Forces", "Hayat Tahrir al-Sham",
            "Recep Tayyip Erdogan", "Vladimir Putin", "Kurdish People's Protection Units",
            "Idlib Governorate", "Northeast Syria", "Islamic State of Iraq and the Levant",
            "Abu Bakr al-Baghdadi", "Mazloum Abdi", "Ras al-Ayn"
        ],
        "event_keywords": [
            "Turkish offensive into northeast Syria October 2019",
            "Battle of Baghuz Fawqani", "Barisha raid killing of al-Baghdadi",
            "Idlib offensive 2019-2020", "Sochi memorandum Turkey Russia",
            "M4 highway joint patrols"
        ],
        "broader_context": [
            "United States troop withdrawal from Syria", "Autonomous Administration of North and East Syria",
            "Caesar Syria Civilian Protection Act", "Syrian refugee crisis"
        ],
    },
    "c1_c_yemen": {
        "canonical_keywords": ["Yemeni civil war", "Saudi-led intervention in Yemen"],
        "entity_keywords": [
            "Houthi movement", "Ansar Allah", "Abdrabbuh Mansur Hadi", "Mohammed bin Salman",
            "Saudi Arabia", "United Arab Emirates", "Abdul-Malik al-Houthi",
            "Aden", "Sanaa", "Southern Transitional Council", "Hodeidah",
            "Saudi-led coalition", "Stockholm Agreement"
        ],
        "event_keywords": [
            "Abqaiq-Khurais drone attacks September 2019", "Aden clashes August 2019",
            "Riyadh Agreement November 2019", "Battle of Marib",
            "UAE military drawdown from Yemen"
        ],
        "broader_context": [
            "Yemen humanitarian crisis", "cholera outbreak in Yemen",
            "United Nations-led peace process", "US arms sales debate"
        ],
    },
    "c1_d_israel_palestine": {
        "canonical_keywords": ["Israeli–Palestinian conflict", "Gaza-Israel escalation 2019"],
        "entity_keywords": [
            "Benjamin Netanyahu", "Mahmoud Abbas", "Hamas", "Palestinian Islamic Jihad",
            "Yahya Sinwar", "Gaza Strip", "West Bank", "Jared Kushner", "Donald Trump",
            "Bahaa Abu al-Ata", "Ismail Haniyeh", "Israel Defense Forces"
        ],
        "event_keywords": [
            "Trump peace plan unveiling January 2020", "killing of Bahaa Abu al-Ata November 2019",
            "Great March of Return", "Operation Black Belt November 2019",
            "Israeli annexation plan for the West Bank"
        ],
        "broader_context": [
            "Abraham Accords normalization", "Israeli settlement expansion",
            "Israeli political deadlock 2019-2020", "blockade of the Gaza Strip"
        ],
    },

    # ===== c2: South Asia 2024-2025 =====
    "c2_a_operation_sindoor": {
        "canonical_keywords": ["Operation Sindoor", "2025 India-Pakistan crisis"],
        "entity_keywords": [
            "Indian Armed Forces", "Pakistan Armed Forces", "Narendra Modi", "Rajnath Singh",
            "Shehbaz Sharif", "Asim Munir", "Lashkar-e-Taiba", "Jaish-e-Mohammed",
            "Bahawalpur", "Muridke", "Pahalgam", "Vikram Misri", "Indian Air Force",
            "S. Jaishankar"
        ],
        "event_keywords": [
            "Pahalgam terror attack April 2025", "Indian missile strikes May 7 2025",
            "Pakistani retaliation Operation Bunyan al-Marsoos",
            "ceasefire announcement May 10 2025", "Indus Waters Treaty suspension",
            "Attari-Wagah border closure"
        ],
        "broader_context": [
            "cross-border terrorism", "Line of Control skirmishes",
            "Indus Waters Treaty", "Kashmir dispute"
        ],
    },
    "c2_b_bangladesh_transition": {
        "canonical_keywords": ["2024 Bangladesh political transition", "fall of the Hasina government"],
        "entity_keywords": [
            "Sheikh Hasina", "Awami League", "Muhammad Yunus",
            "Bangladesh Nationalist Party", "Khaleda Zia", "Waker-uz-Zaman",
            "Students Against Discrimination", "Nahid Islam", "Dhaka", "Ganabhaban",
            "Mohammed Shahabuddin"
        ],
        "event_keywords": [
            "Hasina resignation August 5 2024", "Hasina flight to India",
            "interim government oath August 8 2024", "march to Dhaka",
            "storming of Ganabhaban"
        ],
        "broader_context": [
            "quota reform movement", "Bangladesh-India diplomatic relations",
            "International Crimes Tribunal Bangladesh", "post-transition election planning"
        ],
    },
    "c2_c_afghanistan_taliban": {
        "canonical_keywords": ["Taliban rule in Afghanistan", "Islamic Emirate of Afghanistan"],
        "entity_keywords": [
            "Taliban", "Hibatullah Akhundzada", "Mullah Mohammad Hassan Akhund",
            "Sirajuddin Haqqani", "Kabul", "Kandahar",
            "Islamic State Khorasan Province", "Tehrik-i-Taliban Pakistan",
            "United Nations Assistance Mission in Afghanistan", "Doha"
        ],
        "event_keywords": [
            "girls' secondary education ban", "women university ban December 2022",
            "Kabul mosque bombings", "Pakistan-Afghanistan border clashes",
            "Doha process United Nations meetings"
        ],
        "broader_context": [
            "Afghan refugee crisis", "frozen Afghan central bank assets",
            "humanitarian aid restrictions", "opium poppy cultivation ban"
        ],
    },
    "c2_d_kashmir": {
        "canonical_keywords": ["Kashmir conflict", "Jammu and Kashmir unrest"],
        "entity_keywords": [
            "Jammu and Kashmir", "Line of Control", "Indian Army", "Pakistan Army",
            "The Resistance Front", "Hizb-ul-Mujahideen", "Srinagar", "Pahalgam",
            "Reasi", "Poonch", "Kathua", "Anantnag", "Manoj Sinha"
        ],
        "event_keywords": [
            "Reasi pilgrim bus attack June 2024", "Pahalgam tourist attack April 2025",
            "Kathua army convoy attack", "2024 Jammu and Kashmir Legislative Assembly election",
            "Article 370 Supreme Court verdict December 2023"
        ],
        "broader_context": [
            "abrogation of Article 370", "Jammu and Kashmir Reorganisation Act",
            "infiltration along the Line of Control", "Amarnath Yatra security"
        ],
    },

    # ===== c3: Russia-Ukraine Theater 2022-2024 =====
    "c3_a_ukraine_frontline": {
        "canonical_keywords": ["Russian invasion of Ukraine", "war in Ukraine"],
        "entity_keywords": [
            "Volodymyr Zelensky", "Vladimir Putin", "Valery Zaluzhny", "Oleksandr Syrskyi",
            "Sergei Shoigu", "Bakhmut", "Avdiivka", "Mariupol", "Kherson", "Kharkiv",
            "Kursk Oblast", "Donbas", "Crimea", "Armed Forces of Ukraine"
        ],
        "event_keywords": [
            "Battle of Bakhmut", "fall of Avdiivka February 2024",
            "Kharkiv counteroffensive September 2022", "liberation of Kherson November 2022",
            "Ukrainian Kursk incursion August 2024", "siege of Mariupol",
            "Crimean Bridge attacks"
        ],
        "broader_context": [
            "HIMARS deliveries to Ukraine", "F-16 transfer to Ukraine",
            "ATACMS missile supply", "Black Sea Grain Initiative",
            "Russian partial mobilization"
        ],
    },
    "c3_b_sanctions": {
        "canonical_keywords": ["Sanctions against Russia", "Western sanctions on Russia"],
        "entity_keywords": [
            "European Union", "US Treasury Department",
            "Office of Foreign Assets Control", "Group of Seven", "SWIFT",
            "Sberbank", "VTB Bank", "Central Bank of Russia",
            "Roman Abramovich", "Alisher Usmanov", "Rosneft", "Gazprom"
        ],
        "event_keywords": [
            "SWIFT exclusion of Russian banks", "Russian central bank reserves freeze",
            "G7 oil price cap December 2022", "EU oil embargo on Russia",
            "yacht and asset seizures"
        ],
        "broader_context": [
            "European energy decoupling from Russia", "ruble depreciation",
            "shadow fleet of tankers", "secondary sanctions enforcement"
        ],
    },
    "c3_c_nato_expansion": {
        "canonical_keywords": ["NATO enlargement", "Finland and Sweden NATO accession"],
        "entity_keywords": [
            "Finland", "Sweden", "Sauli Niinistö", "Sanna Marin", "Ulf Kristersson",
            "Magdalena Andersson", "Jens Stoltenberg", "Recep Tayyip Erdogan",
            "Viktor Orbán", "Turkey", "Hungary", "North Atlantic Treaty Organization"
        ],
        "event_keywords": [
            "Finland NATO accession April 4 2023", "Sweden NATO accession March 7 2024",
            "Madrid summit June 2022", "Vilnius summit July 2023",
            "Turkish parliament ratification of Sweden"
        ],
        "broader_context": [
            "Article 5 collective defense", "Nordic defense cooperation",
            "expanded Russia-NATO border", "NATO 2 percent GDP defense target"
        ],
    },
    "c3_d_wagner_prigozhin": {
        "canonical_keywords": ["Wagner Group", "Prigozhin mutiny"],
        "entity_keywords": [
            "Yevgeny Prigozhin", "Dmitry Utkin", "Wagner Group", "Sergei Shoigu",
            "Valery Gerasimov", "Rostov-on-Don", "Voronezh", "Alexander Lukashenko",
            "Tver Oblast"
        ],
        "event_keywords": [
            "Wagner mutiny June 23-24 2023", "march on Moscow",
            "Wagner occupation of Rostov-on-Don", "Prigozhin plane crash August 23 2023",
            "Belarus exile deal"
        ],
        "broader_context": [
            "Russian private military companies", "Wagner operations in Africa",
            "Wagner role in the Battle of Bakhmut", "Russian Ministry of Defence contract dispute"
        ],
    },

    # ===== c4: Israel-Gaza-Lebanon-Iran 2023-2024 =====
    "c4_a_gaza_war": {
        "canonical_keywords": ["2023 Israel-Hamas war", "October 7 attacks"],
        "entity_keywords": [
            "Hamas", "Israel Defense Forces", "Benjamin Netanyahu", "Yahya Sinwar",
            "Yoav Gallant", "Mohammed Deif", "Ismail Haniyeh", "Gaza Strip",
            "Rafah", "Khan Younis", "Nova music festival", "Kibbutz Be'eri",
            "Hostages and Missing Families Forum"
        ],
        "event_keywords": [
            "October 7 Hamas attack on Israel", "Nova music festival massacre",
            "Israeli ground invasion of Gaza", "Al-Shifa Hospital raid",
            "Rafah offensive May 2024", "killing of Yahya Sinwar October 2024",
            "Haniyeh assassination in Tehran July 2024",
            "first hostage release deal November 2023"
        ],
        "broader_context": [
            "Gaza humanitarian crisis", "International Court of Justice genocide case",
            "International Criminal Court arrest warrants",
            "United Nations Relief and Works Agency funding suspension",
            "Philadelphi Corridor"
        ],
    },
    "c4_b_hezbollah_israel": {
        "canonical_keywords": ["2023-2024 Israel-Hezbollah conflict", "Lebanon-Israel border conflict"],
        "entity_keywords": [
            "Hezbollah", "Hassan Nasrallah", "Naim Qassem", "Fuad Shukr",
            "Israel Defense Forces", "Southern Lebanon", "Beirut",
            "Dahieh", "Litani River", "United Nations Interim Force in Lebanon",
            "Tyre", "Nabatieh"
        ],
        "event_keywords": [
            "Hezbollah pager attack September 17 2024",
            "walkie-talkie explosions September 18 2024",
            "killing of Hassan Nasrallah September 27 2024",
            "Israeli ground invasion of southern Lebanon October 2024",
            "Fuad Shukr assassination Beirut July 2024",
            "Majdal Shams rocket strike"
        ],
        "broader_context": [
            "Blue Line border", "2006 Lebanon War legacy",
            "Lebanese government caretaker status", "Iran-led Axis of Resistance",
            "displacement in northern Israel"
        ],
    },
    "c4_c_houthi_red_sea": {
        "canonical_keywords": ["Houthi attacks in the Red Sea", "Red Sea shipping crisis"],
        "entity_keywords": [
            "Houthi movement", "Ansar Allah", "Abdul-Malik al-Houthi",
            "Bab el-Mandeb", "Galaxy Leader", "Red Sea", "Gulf of Aden",
            "USS Carney", "USS Dwight D. Eisenhower",
            "Operation Prosperity Guardian", "Maersk", "Suez Canal Authority"
        ],
        "event_keywords": [
            "Galaxy Leader hijacking November 2023",
            "Operation Prosperity Guardian launch December 2023",
            "US-UK strikes on Yemen January 2024", "MV Tutor sinking",
            "MV Rubymar sinking", "Operation Poseidon Archer"
        ],
        "broader_context": [
            "global shipping disruption", "Suez Canal traffic decline",
            "Cape of Good Hope rerouting", "Iranian weapons supply to the Houthis"
        ],
    },
    "c4_d_iran_strikes": {
        "canonical_keywords": ["April 2024 Iranian strikes against Israel", "October 2024 Iranian strikes against Israel"],
        "entity_keywords": [
            "Islamic Revolutionary Guard Corps", "Israeli Air Force",
            "Ayatollah Ali Khamenei", "Hossein Salami", "Mohammad Reza Zahedi",
            "Damascus", "Isfahan", "Nevatim Airbase", "Iron Dome", "Arrow 3", "David's Sling"
        ],
        "event_keywords": [
            "Damascus consulate strike April 1 2024",
            "Operation True Promise April 13 2024",
            "Isfahan strike April 19 2024",
            "Operation True Promise II October 1 2024",
            "Israeli retaliation October 26 2024"
        ],
        "broader_context": [
            "Iranian nuclear program", "Axis of Resistance",
            "ballistic missile defense", "regional escalation risk"
        ],
    },

    # ===== c5: China-Taiwan-US Tech 2022-2024 =====
    "c5_a_taiwan_strait": {
        "canonical_keywords": ["Taiwan Strait crisis", "China-Taiwan tensions"],
        "entity_keywords": [
            "Tsai Ing-wen", "Lai Ching-te", "Xi Jinping", "Nancy Pelosi",
            "People's Liberation Army", "PLA Eastern Theater Command",
            "Taiwan Strait median line", "Kinmen", "Matsu",
            "Democratic Progressive Party", "Kuomintang", "Joint Sword exercises"
        ],
        "event_keywords": [
            "Pelosi visit to Taiwan August 2022",
            "Joint Sword 2024A exercises", "Joint Sword 2024B exercises",
            "Taiwan presidential election January 2024",
            "Lai Ching-te inauguration May 2024"
        ],
        "broader_context": [
            "One China policy", "Taiwan Relations Act",
            "AUKUS partnership", "semiconductor supply chain",
            "United States Indo-Pacific Strategy"
        ],
    },
    "c5_b_chip_export_controls": {
        "canonical_keywords": ["United States export controls on semiconductors to China", "chip export controls"],
        "entity_keywords": [
            "Bureau of Industry and Security", "Gina Raimondo",
            "ASML Holding", "Taiwan Semiconductor Manufacturing Company",
            "Semiconductor Manufacturing International Corporation",
            "Huawei", "Nvidia", "Jensen Huang",
            "CHIPS and Science Act", "Yangtze Memory Technologies",
            "Entity List", "Foreign Direct Product Rule"
        ],
        "event_keywords": [
            "October 2022 chip export controls",
            "October 2023 chip export controls update",
            "Huawei Mate 60 Pro launch",
            "ASML extreme ultraviolet lithography restrictions",
            "Nvidia H20 chip restrictions"
        ],
        "broader_context": [
            "semiconductor supply chain decoupling",
            "CHIPS Act manufacturing subsidies",
            "indigenous Chinese chip development",
            "advanced node manufacturing"
        ],
    },
    "c5_c_hong_kong": {
        "canonical_keywords": ["Hong Kong national security law", "Article 23 legislation"],
        "entity_keywords": [
            "John Lee", "Carrie Lam", "Jimmy Lai", "Apple Daily",
            "Joshua Wong", "Benny Tai",
            "Hong Kong Legislative Council",
            "Standing Committee of the National People's Congress",
            "Hong Kong 47", "Stand News"
        ],
        "event_keywords": [
            "Hong Kong 47 trial", "Jimmy Lai national security trial",
            "Stand News sedition verdict",
            "Safeguarding National Security Ordinance March 2024",
            "patriots-only electoral reform"
        ],
        "broader_context": [
            "one country two systems", "2019 Hong Kong protests aftermath",
            "British National Overseas visa emigration",
            "rule of law concerns Hong Kong"
        ],
    },
    "c5_d_south_china_sea": {
        "canonical_keywords": ["South China Sea disputes", "Philippines-China maritime tensions"],
        "entity_keywords": [
            "Ferdinand Marcos Jr.", "Philippine Coast Guard", "China Coast Guard",
            "Second Thomas Shoal", "Scarborough Shoal", "BRP Sierra Madre",
            "Spratly Islands", "Paracel Islands", "nine-dash line",
            "Association of Southeast Asian Nations", "Vietnam", "Malaysia"
        ],
        "event_keywords": [
            "Second Thomas Shoal water cannon incidents",
            "Scarborough Shoal standoff",
            "Philippines-China June 17 2024 clash",
            "BRP Sierra Madre resupply missions"
        ],
        "broader_context": [
            "United Nations Convention on the Law of the Sea arbitration ruling 2016",
            "United States-Philippines Mutual Defense Treaty",
            "Enhanced Defense Cooperation Agreement",
            "freedom of navigation operations"
        ],
    },

    # ===== c6: US Election 2024 =====
    "c6_a_trump_campaign": {
        "canonical_keywords": ["Donald Trump 2024 presidential campaign", "Trump criminal trials"],
        "entity_keywords": [
            "Donald Trump", "JD Vance", "Alvin Bragg", "Jack Smith", "Fani Willis",
            "Letitia James", "Aileen Cannon", "Juan Merchan",
            "Mar-a-Lago", "Stormy Daniels", "Michael Cohen", "E. Jean Carroll"
        ],
        "event_keywords": [
            "Manhattan hush money conviction May 30 2024",
            "Mar-a-Lago classified documents indictment",
            "January 6 federal indictment",
            "Georgia racketeering indictment",
            "New York civil fraud judgment",
            "JD Vance vice presidential selection"
        ],
        "broader_context": [
            "Republican National Convention Milwaukee", "Project 2025 policy agenda",
            "Supreme Court presidential immunity ruling",
            "Fourteenth Amendment Section 3 Colorado ballot case"
        ],
    },
    "c6_b_biden_harris": {
        "canonical_keywords": ["Joe Biden withdrawal from 2024 race", "Kamala Harris 2024 presidential campaign"],
        "entity_keywords": [
            "Joe Biden", "Kamala Harris", "Tim Walz", "Jill Biden", "Doug Emhoff",
            "Democratic National Committee", "Jaime Harrison",
            "Pete Buttigieg", "Josh Shapiro", "Mark Kelly"
        ],
        "event_keywords": [
            "Biden-Trump first debate June 27 2024",
            "Biden withdrawal announcement July 21 2024",
            "Harris endorsement by Biden",
            "Walz vice presidential selection August 6 2024",
            "Democratic National Convention Chicago August 2024",
            "Harris-Trump debate September 10 2024"
        ],
        "broader_context": [
            "concerns over Biden's age and fitness",
            "Democratic Party delegate process",
            "presidential campaign fundraising records",
            "post-Dobbs abortion politics"
        ],
    },
    "c6_c_congressional_races": {
        "canonical_keywords": [
            "2024 United States House of Representatives elections",
            "2024 United States Senate elections"
        ],
        "entity_keywords": [
            "Mike Johnson", "Hakeem Jeffries", "Chuck Schumer", "Mitch McConnell",
            "John Thune", "Sherrod Brown", "Jon Tester",
            "Bernie Moreno", "Tim Sheehy", "Larry Hogan",
            "Colin Allred", "Ted Cruz", "Bob Casey", "David McCormick"
        ],
        "event_keywords": [
            "Republican Senate majority flip",
            "Ohio Senate race Brown loss to Moreno",
            "Montana Senate race Tester loss to Sheehy",
            "House Republican majority retention",
            "Pennsylvania Senate race Casey-McCormick"
        ],
        "broader_context": [
            "redistricting and gerrymandering",
            "split-ticket voting", "campaign finance super political action committees",
            "Senate filibuster debate"
        ],
    },
    "c6_d_assassination_attempts": {
        "canonical_keywords": [
            "Attempted assassination of Donald Trump in Pennsylvania",
            "Butler rally shooting"
        ],
        "entity_keywords": [
            "Thomas Matthew Crooks", "Donald Trump",
            "United States Secret Service", "Kimberly Cheatle", "Ronald Rowe",
            "Butler Farm Show grounds", "Corey Comperatore",
            "Ryan Wesley Routh", "Trump International Golf Club West Palm Beach"
        ],
        "event_keywords": [
            "Butler Pennsylvania rally shooting July 13 2024",
            "Cheatle resignation July 23 2024",
            "West Palm Beach golf course incident September 15 2024",
            "Senate Judiciary Committee hearings"
        ],
        "broader_context": [
            "Secret Service security failures",
            "House Task Force on the Attempted Assassination",
            "campaign rally security",
            "political violence in the United States"
        ],
    },

    # ===== c7: European Political Shifts 2024 =====
    "c7_a_uk_election": {
        "canonical_keywords": ["2024 United Kingdom general election", "Labour landslide 2024"],
        "entity_keywords": [
            "Keir Starmer", "Rishi Sunak", "Ed Davey", "Nigel Farage", "John Swinney",
            "Labour Party", "Conservative Party", "Liberal Democrats",
            "Reform UK", "Scottish National Party", "10 Downing Street"
        ],
        "event_keywords": [
            "election announcement May 22 2024",
            "polling day July 4 2024",
            "Labour majority of 174 seats",
            "Conservative collapse to 121 seats",
            "Reform UK five-seat breakthrough",
            "Liz Truss seat loss"
        ],
        "broader_context": [
            "Conservative leadership turmoil 2022-2024",
            "cost of living crisis", "National Health Service waiting lists",
            "post-Brexit politics"
        ],
    },
    "c7_b_france_snap": {
        "canonical_keywords": ["2024 French legislative election", "France snap election"],
        "entity_keywords": [
            "Emmanuel Macron", "Gabriel Attal", "Michel Barnier",
            "Marine Le Pen", "Jordan Bardella", "Jean-Luc Mélenchon",
            "Rassemblement National", "Nouveau Front Populaire",
            "Ensemble", "La France Insoumise", "Élysée Palace"
        ],
        "event_keywords": [
            "dissolution of the National Assembly June 9 2024",
            "first round June 30 2024", "second round July 7 2024",
            "republican front against Rassemblement National",
            "Barnier government appointment",
            "Barnier no-confidence vote December 2024"
        ],
        "broader_context": [
            "European Parliament results in France",
            "hung parliament", "French political polarization",
            "pension reform protests legacy"
        ],
    },
    "c7_c_germany_coalition": {
        "canonical_keywords": ["Collapse of the Scholz government", "2025 German federal election"],
        "entity_keywords": [
            "Olaf Scholz", "Christian Lindner", "Robert Habeck",
            "Friedrich Merz", "Alice Weidel",
            "Social Democratic Party of Germany", "Free Democratic Party",
            "Alliance 90/The Greens", "CDU/CSU", "Alternative for Germany",
            "Bundestag", "Frank-Walter Steinmeier"
        ],
        "event_keywords": [
            "Lindner dismissal November 6 2024",
            "Free Democratic Party exit from coalition",
            "Bundestag confidence vote December 16 2024",
            "snap election February 23 2025",
            "CDU/CSU election victory"
        ],
        "broader_context": [
            "traffic light coalition Ampel",
            "German debt brake constitutional dispute",
            "Ukraine military aid debate", "German industrial slowdown"
        ],
    },
    "c7_d_eu_parliament": {
        "canonical_keywords": ["2024 European Parliament election", "EU Parliament far-right gains"],
        "entity_keywords": [
            "Ursula von der Leyen", "Roberta Metsola",
            "European People's Party",
            "Progressive Alliance of Socialists and Democrats",
            "Identity and Democracy", "European Conservatives and Reformists",
            "Patriots for Europe", "Renew Europe",
            "Manfred Weber", "António Costa", "Kaja Kallas"
        ],
        "event_keywords": [
            "European Parliament elections June 6-9 2024",
            "Patriots for Europe group formation",
            "von der Leyen reelection as Commission President",
            "new College of Commissioners 2024",
            "Rassemblement National first place in France"
        ],
        "broader_context": [
            "European Green Deal backlash",
            "EU migration policy debate",
            "European Union enlargement to Ukraine",
            "Spitzenkandidat process"
        ],
    },

    # ===== c8: Bangladesh Political Upheaval 2024-2025 =====
    "c8_a_quota_protests": {
        "canonical_keywords": ["2024 Bangladesh quota reform movement", "Bangladesh student protests"],
        "entity_keywords": [
            "Students Against Discrimination", "Nahid Islam", "Asif Mahmud",
            "Sheikh Hasina", "Awami League", "Bangladesh Chhatra League",
            "University of Dhaka", "Rangpur", "Abu Sayed", "razakar"
        ],
        "event_keywords": [
            "High Court quota reinstatement June 2024",
            "Hasina razakar comment July 14 2024",
            "killing of Abu Sayed in Rangpur July 16 2024",
            "Bangladesh nationwide internet shutdown",
            "Supreme Court quota ruling July 21 2024",
            "non-cooperation movement August 2024"
        ],
        "broader_context": [
            "1971 freedom fighters' descendants quota",
            "Bangladesh civil service recruitment",
            "youth unemployment in Bangladesh",
            "University of Dhaka student politics"
        ],
    },
    "c8_b_hasina_fall": {
        "canonical_keywords": ["Resignation of Sheikh Hasina", "Fall of the Hasina government"],
        "entity_keywords": [
            "Sheikh Hasina", "Sajeeb Wazed Joy", "Waker-uz-Zaman",
            "Mohammed Shahabuddin", "Awami League", "Ganabhaban",
            "Hindon Air Base", "Bangabhaban", "Obaidul Quader"
        ],
        "event_keywords": [
            "march to Dhaka August 5 2024",
            "Hasina helicopter departure from Dhaka",
            "storming of Ganabhaban",
            "Hindon Air Base landing in India",
            "army chief national address August 5 2024",
            "parliament dissolution August 6 2024"
        ],
        "broader_context": [
            "fifteen years of Awami League rule",
            "extrajudicial killings allegations",
            "post-transition election timeline",
            "India-Bangladesh asylum question"
        ],
    },
    "c8_c_yunus_interim": {
        "canonical_keywords": ["Yunus interim government", "Bangladesh interim government 2024"],
        "entity_keywords": [
            "Muhammad Yunus", "Grameen Bank", "Asif Nazrul",
            "Nahid Islam", "Md. Touhid Hossain", "Salehuddin Ahmed",
            "Council of Advisers", "Bangabhaban",
            "Bangladesh Election Commission", "Constitution Reform Commission"
        ],
        "event_keywords": [
            "Yunus oath as Chief Adviser August 8 2024",
            "Council of Advisers formation",
            "establishment of reform commissions",
            "election timeline announcement",
            "Awami League political activities suspension"
        ],
        "broader_context": [
            "Grameen Bank microfinance",
            "Nobel Peace Prize 2006",
            "Bangladesh judicial reform",
            "International Crimes Tribunal Hasina trial"
        ],
    },
    "c8_d_minority_attacks": {
        "canonical_keywords": [
            "Attacks on Hindus in Bangladesh 2024",
            "Bangladesh communal violence 2024"
        ],
        "entity_keywords": [
            "Bangladesh Hindu Buddhist Christian Unity Council",
            "Chinmoy Krishna Das", "International Society for Krishna Consciousness",
            "Indian Ministry of External Affairs", "S. Jaishankar",
            "Randhir Jaiswal", "Chittagong", "Rangpur",
            "Saiful Islam Alif", "Agartala"
        ],
        "event_keywords": [
            "temple and home attacks August 2024",
            "Chinmoy Krishna Das arrest November 2024",
            "lawyer Saiful Islam killing in Chittagong",
            "Tripura Bangladesh consulate breach November 2024",
            "Akhaura border tensions"
        ],
        "broader_context": [
            "Hindu population decline in Bangladesh",
            "history of communal violence",
            "India-Bangladesh diplomatic strain",
            "Durga Puja security arrangements"
        ],
    },

    # ===== c9: 2023 Disaster Year =====
    "c9_a_turkey_syria_eq": {
        "canonical_keywords": ["2023 Turkey-Syria earthquakes", "Kahramanmaraş earthquakes"],
        "entity_keywords": [
            "Recep Tayyip Erdogan", "Bashar al-Assad",
            "Disaster and Emergency Management Presidency", "Turkish Red Crescent",
            "White Helmets", "Kahramanmaraş", "Gaziantep", "Hatay",
            "Antakya", "Adıyaman", "Aleppo", "Idlib"
        ],
        "event_keywords": [
            "magnitude 7.8 earthquake February 6 2023",
            "magnitude 7.5 aftershock earthquake",
            "destruction of Antakya",
            "Bab al-Hawa border crossing aid",
            "construction contractor arrests",
            "May 2023 Turkish presidential election impact"
        ],
        "broader_context": [
            "Turkish building code violations",
            "humanitarian aid access to opposition-held Syria",
            "earthquake reconstruction zone",
            "North Anatolian and East Anatolian fault zones"
        ],
    },
    "c9_b_morocco_eq": {
        "canonical_keywords": ["2023 Marrakesh-Safi earthquake", "Al Haouz earthquake"],
        "entity_keywords": [
            "King Mohammed VI", "Aziz Akhannouch", "Marrakesh",
            "Al Haouz Province", "Atlas Mountains",
            "Royal Moroccan Armed Forces", "Tinmel Mosque",
            "Amizmiz", "Talat N'Yaaqoub", "Asni"
        ],
        "event_keywords": [
            "magnitude 6.8 earthquake September 8 2023",
            "Tinmel Mosque collapse",
            "Marrakesh medina damage",
            "Atlas Mountain villages destruction",
            "five-day national mourning declaration"
        ],
        "broader_context": [
            "controversy over foreign aid acceptance",
            "rural infrastructure in Morocco",
            "2030 FIFA World Cup preparations",
            "Amazigh Berber communities"
        ],
    },
    "c9_c_libya_floods": {
        "canonical_keywords": ["Storm Daniel Libya floods", "Derna dam collapse"],
        "entity_keywords": [
            "Storm Daniel", "Derna", "Wadi Derna",
            "Abu Mansour Dam", "Al-Bilad Dam",
            "Government of National Unity", "Abdul Hamid Dbeibeh",
            "Libyan National Army", "Khalifa Haftar", "Aguila Saleh"
        ],
        "event_keywords": [
            "Storm Daniel landfall September 10 2023",
            "two-dam collapse in Derna",
            "destruction of central Derna",
            "international rescue teams arrival",
            "anti-government protests in Derna"
        ],
        "broader_context": [
            "Libyan east-west political division",
            "dam maintenance neglect",
            "Mediterranean medicane storms",
            "post-Gaddafi Libya governance"
        ],
    },
    "c9_d_maui_fires": {
        "canonical_keywords": ["2023 Hawaii wildfires", "Lahaina fire"],
        "entity_keywords": [
            "Lahaina", "Maui", "Hawaiian Electric", "Josh Green",
            "Richard Bissen", "Maui Emergency Management Agency",
            "Herman Andaya", "Front Street Lahaina", "Banyan Court",
            "Kula", "Federal Emergency Management Agency"
        ],
        "event_keywords": [
            "Lahaina fire August 8 2023",
            "Front Street destruction",
            "downed power line ignition",
            "missing persons list release",
            "Herman Andaya resignation",
            "Hawaiian Electric lawsuits",
            "Maui fire global settlement August 2024"
        ],
        "broader_context": [
            "Hurricane Dora wind effects",
            "invasive grass fuel load",
            "emergency siren controversy",
            "Native Hawaiian land rights",
            "Maui tourism reopening debate"
        ],
    },

    # ===== c10: COVID-19 & Co-occurring Crises 2020-2021 =====
    "c10_a_covid_pandemic": {
        "canonical_keywords": ["COVID-19 pandemic", "coronavirus pandemic"],
        "entity_keywords": [
            "World Health Organization", "Tedros Adhanom Ghebreyesus",
            "Anthony Fauci", "Centers for Disease Control and Prevention",
            "Wuhan", "SARS-CoV-2", "Delta variant", "Omicron variant",
            "Boris Johnson", "Andrew Cuomo", "Narendra Modi", "Xi Jinping"
        ],
        "event_keywords": [
            "World Health Organization pandemic declaration March 11 2020",
            "Wuhan lockdown January 2020",
            "Italy nationwide lockdown March 2020",
            "India Delta wave April-May 2021",
            "Omicron variant emergence November 2021",
            "Shanghai lockdown 2022"
        ],
        "broader_context": [
            "China zero-COVID policy",
            "lab leak hypothesis",
            "global supply chain disruptions",
            "remote work transition",
            "long COVID"
        ],
    },
    "c10_b_vaccine_rollout": {
        "canonical_keywords": ["COVID-19 vaccine development", "COVID-19 vaccine rollout"],
        "entity_keywords": [
            "Pfizer-BioNTech", "Moderna", "AstraZeneca",
            "Johnson & Johnson", "Sinovac", "Sinopharm",
            "Covaxin", "Sputnik V", "Operation Warp Speed", "COVAX",
            "Albert Bourla", "Stéphane Bancel", "Uğur Şahin"
        ],
        "event_keywords": [
            "Pfizer emergency use authorization December 2020",
            "Moderna emergency use authorization December 2020",
            "first vaccinations United Kingdom December 8 2020",
            "AstraZeneca blood clot concerns",
            "booster shot rollout 2021",
            "vaccine mandate protests"
        ],
        "broader_context": [
            "messenger RNA vaccine technology",
            "vaccine inequity in the Global South",
            "TRIPS waiver debate",
            "anti-vaccine misinformation"
        ],
    },
    "c10_c_blm_protests": {
        "canonical_keywords": ["George Floyd protests", "2020 Black Lives Matter protests"],
        "entity_keywords": [
            "George Floyd", "Derek Chauvin", "Minneapolis",
            "Minneapolis Police Department", "Black Lives Matter",
            "Breonna Taylor", "Ahmaud Arbery", "Jacob Blake",
            "Kenosha", "Lafayette Square", "Portland Oregon", "Tim Walz"
        ],
        "event_keywords": [
            "killing of George Floyd May 25 2020",
            "burning of Minneapolis Third Precinct",
            "Lafayette Square clearing June 1 2020",
            "Chauvin conviction April 2021",
            "Capitol Hill Organized Protest Seattle",
            "removal of Confederate monuments"
        ],
        "broader_context": [
            "police reform debate",
            "defund the police movement",
            "qualified immunity",
            "Confederate statue removal"
        ],
    },
    "c10_d_capitol_jan6": {
        "canonical_keywords": [
            "January 6 United States Capitol attack",
            "2021 storming of the United States Capitol"
        ],
        "entity_keywords": [
            "Donald Trump", "Mike Pence", "Nancy Pelosi",
            "United States Capitol Police", "Brian Sicknick", "Ashli Babbitt",
            "Proud Boys", "Oath Keepers", "Stewart Rhodes", "Enrique Tarrio",
            "Liz Cheney", "Bennie Thompson"
        ],
        "event_keywords": [
            "Save America rally at the Ellipse",
            "Capitol breach January 6 2021",
            "joint session of Congress interruption",
            "Ashli Babbitt shooting",
            "Trump second impeachment",
            "January 6 Select Committee hearings",
            "Oath Keepers seditious conspiracy convictions"
        ],
        "broader_context": [
            "2020 election fraud claims",
            "Stop the Steal movement",
            "presidential transition certification",
            "Electoral Count Reform Act"
        ],
    },

    # ===== c11: AI Boom 2022-2024 =====
    "c11_a_chatgpt_openai": {
        "canonical_keywords": ["ChatGPT", "launch of ChatGPT"],
        "entity_keywords": [
            "OpenAI", "Sam Altman", "Greg Brockman", "Ilya Sutskever",
            "Mira Murati", "Generative Pre-trained Transformer 3.5",
            "Generative Pre-trained Transformer 4",
            "Microsoft", "Satya Nadella", "InstructGPT",
            "reinforcement learning from human feedback"
        ],
        "event_keywords": [
            "ChatGPT public release November 30 2022",
            "GPT-4 release March 14 2023",
            "ChatGPT 100 million users milestone January 2023",
            "ChatGPT Plus subscription launch February 2023",
            "GPT Store launch January 2024"
        ],
        "broader_context": [
            "large language models",
            "Microsoft-OpenAI partnership",
            "Bing chat integration",
            "AI safety debate"
        ],
    },
    "c11_b_altman_ouster": {
        "canonical_keywords": [
            "Removal of Sam Altman from OpenAI",
            "OpenAI November 2023 board crisis"
        ],
        "entity_keywords": [
            "Sam Altman", "Greg Brockman", "Ilya Sutskever", "Mira Murati",
            "Helen Toner", "Tasha McCauley", "Adam D'Angelo",
            "Bret Taylor", "Larry Summers", "Emmett Shear",
            "Satya Nadella"
        ],
        "event_keywords": [
            "Altman firing November 17 2023",
            "Murati interim CEO appointment",
            "OpenAI employee letter signed by 95 percent of staff",
            "Microsoft job offer to Altman",
            "Altman reinstatement November 21 2023",
            "new OpenAI board formation"
        ],
        "broader_context": [
            "OpenAI nonprofit governance structure",
            "AI safety versus commercialization tension",
            "Q* project rumors",
            "OpenAI superalignment team"
        ],
    },
    "c11_c_eu_ai_act": {
        "canonical_keywords": ["European Union Artificial Intelligence Act", "EU AI Act"],
        "entity_keywords": [
            "European Commission", "European Parliament",
            "Council of the European Union",
            "Thierry Breton", "Margrethe Vestager",
            "Brando Benifei", "Dragoș Tudorache",
            "European AI Office", "European Artificial Intelligence Board"
        ],
        "event_keywords": [
            "AI Act political agreement December 8 2023",
            "European Parliament adoption March 13 2024",
            "Council approval May 21 2024",
            "Official Journal publication July 12 2024",
            "AI Act entry into force August 1 2024"
        ],
        "broader_context": [
            "risk-based regulation",
            "general-purpose AI rules",
            "foundation model obligations",
            "Brussels effect on global AI regulation"
        ],
    },
    "c11_d_big_tech_ai": {
        "canonical_keywords": ["Big Tech AI product launches", "AI race 2023-2024"],
        "entity_keywords": [
            "Google", "Sundar Pichai", "Demis Hassabis", "Google DeepMind",
            "Gemini", "Bard", "Meta Platforms", "Mark Zuckerberg",
            "Llama", "Anthropic", "Dario Amodei", "Claude",
            "Microsoft Copilot", "Amazon Bedrock"
        ],
        "event_keywords": [
            "Google Bard launch March 2023",
            "Gemini launch December 2023",
            "Llama 2 release July 2023",
            "Llama 3 release April 2024",
            "Claude 3 family launch March 2024",
            "Microsoft Copilot launch",
            "Apple Intelligence WWDC June 2024"
        ],
        "broader_context": [
            "foundation model competition",
            "open-weight versus closed model debate",
            "Nvidia GPU supply constraints",
            "AI compute scaling"
        ],
    },

    # ===== c12: Crypto Collapse 2022-2024 =====
    "c12_a_ftx_sbf": {
        "canonical_keywords": ["FTX collapse", "Sam Bankman-Fried trial"],
        "entity_keywords": [
            "Sam Bankman-Fried", "FTX", "Alameda Research",
            "Caroline Ellison", "Gary Wang", "Nishad Singh",
            "Damian Williams", "Lewis A. Kaplan", "John J. Ray III",
            "Bahamas", "Changpeng Zhao"
        ],
        "event_keywords": [
            "FTX bankruptcy filing November 11 2022",
            "Bankman-Fried Bahamas arrest December 12 2022",
            "Bankman-Fried federal trial October 2023",
            "Bankman-Fried conviction November 2 2023",
            "Bankman-Fried 25-year sentence March 2024",
            "Caroline Ellison sentencing"
        ],
        "broader_context": [
            "customer fund commingling",
            "crypto exchange runs",
            "Effective Altruism associations",
            "FTX political donations"
        ],
    },
    "c12_b_terra_luna": {
        "canonical_keywords": ["Terra Luna crash", "collapse of TerraUSD"],
        "entity_keywords": [
            "Do Kwon", "Terraform Labs", "TerraUSD", "Luna",
            "Anchor Protocol", "Singapore", "Montenegro",
            "Daniel Shin", "United States Securities and Exchange Commission",
            "South Korea Financial Services Commission"
        ],
        "event_keywords": [
            "TerraUSD depeg May 9 2022",
            "Luna hyperinflation crash",
            "Terra blockchain halt",
            "Do Kwon Montenegro arrest March 2023",
            "Terraform Labs SEC settlement"
        ],
        "broader_context": [
            "algorithmic stablecoin failure",
            "2022 crypto contagion",
            "Three Arrows Capital collapse",
            "Celsius Network bankruptcy"
        ],
    },
    "c12_c_binance_cz": {
        "canonical_keywords": ["Binance settlement", "Changpeng Zhao guilty plea"],
        "entity_keywords": [
            "Changpeng Zhao", "Binance",
            "United States Department of Justice",
            "United States Treasury Department",
            "Financial Crimes Enforcement Network",
            "Office of Foreign Assets Control",
            "Commodity Futures Trading Commission",
            "Richard Teng", "Merrick Garland", "Janet Yellen"
        ],
        "event_keywords": [
            "Binance $4.3 billion settlement November 2023",
            "Zhao guilty plea Bank Secrecy Act",
            "Zhao resignation as Binance CEO",
            "Zhao four-month sentence April 2024",
            "Richard Teng appointment as CEO"
        ],
        "broader_context": [
            "anti-money laundering compliance",
            "United States crypto exchange regulation",
            "Binance.US separation",
            "Bank Secrecy Act violations"
        ],
    },
    "c12_d_bitcoin_etf": {
        "canonical_keywords": [
            "Spot Bitcoin ETF approval",
            "United States spot bitcoin exchange-traded fund"
        ],
        "entity_keywords": [
            "United States Securities and Exchange Commission", "Gary Gensler",
            "BlackRock", "Larry Fink", "Fidelity Investments", "Grayscale Investments",
            "ARK Invest", "Cathie Wood", "Bitwise Asset Management", "VanEck",
            "iShares Bitcoin Trust"
        ],
        "event_keywords": [
            "Grayscale court victory August 2023",
            "spot Bitcoin ETF approvals January 10 2024",
            "spot Bitcoin ETF trading launch January 11 2024",
            "iShares Bitcoin Trust $10 billion AUM milestone",
            "spot Ether ETF approval May 2024"
        ],
        "broader_context": [
            "Bitcoin halving April 2024",
            "institutional crypto adoption",
            "Grayscale Bitcoin Trust discount to net asset value",
            "Bitcoin futures ETF predecessors"
        ],
    },
}


# ---------- WRITE FILES ----------
def main():
    root = Path(".")

    # Load cluster_config.json to get the canonical subtopic ordering per cluster
    with open("cluster_config.json", "r") as f:
        config = json.load(f)

    written = 0
    missing_cluster_dirs = []

    for cluster in config["clusters"]:
        cluster_id = cluster["cluster_id"]

        # Find the cluster folder by cX_ prefix (matches whatever <name> you used)
        matches = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(f"{cluster_id}_")]
        if len(matches) != 1:
            missing_cluster_dirs.append(cluster_id)
            continue
        cluster_dir = matches[0]

        for sub in cluster["subtopics"]:
            sub_id = sub["id"]
            if cluster_id == "c9":
                print(f"⏭️  Skipping {sub_id} (c9 already curated)")
                continue
            sub_dir = cluster_dir / "subtopics" / sub_id

            data = {
                "subtopic_id": sub_id,
                "canonical_keywords": KEYWORDS[sub_id]["canonical_keywords"],
                "entity_keywords": KEYWORDS[sub_id]["entity_keywords"],
                "event_keywords": KEYWORDS[sub_id]["event_keywords"],
                "broader_context": KEYWORDS[sub_id]["broader_context"],
            }

            out_path = sub_dir / "keywords.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Wrote {out_path}")
            written += 1

    print(f"\nDone. Wrote {written} keywords.json files.")
    if missing_cluster_dirs:
        print(f"⚠️  Skipped clusters (folder not found or ambiguous): {missing_cluster_dirs}")


if __name__ == "__main__":
    main()