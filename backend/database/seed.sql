-- DaryaSagar Seed Data

-- ==============================================
-- SPECIES DATABASE
-- ==============================================
INSERT INTO species (id, names, scientific_name, family, habitat, seasonality, states)
VALUES
('bangda_mackerel',
 '{"mr": "बांगडा", "gu": "બાંગડો", "hi": "बांगडा", "kn": "ಬಾಂಗ್ಡ", "ml": "അയല", "en": "Indian Mackerel", "kok": "बांगडो"}',
 'Rastrelliger kanagurta', 'Scombridae',
 '{"sst_range": [26, 30], "depth_range": [20, 200], "chlorophyll_min": 0.5}',
 '{"maharashtra": ["Aug-Mar"], "goa": ["Jul-Feb"], "karnataka": ["Jul-Feb"], "kerala": ["Year-round"]}',
 '["gujarat", "maharashtra", "goa", "karnataka", "kerala"]'),

('pomfret',
 '{"mr": "पापलेट", "gu": "પાપ્ ‍लेट", "hi": "पापलेट", "kn": "ಅವೋಲಿ", "ml": "ആവോലി", "en": "Pomfret", "kok": "पापलेट"}',
 'Pampus argenteus', 'Stromateidae',
 '{"sst_range": [24, 28], "depth_range": [10, 100]}',
 '{"gujarat": ["Oct-Feb"], "maharashtra": ["Sep-Mar"]}',
 '["gujarat", "maharashtra"]'),

('bombay_duck',
 '{"mr": "बोंबील", "gu": "બોંbil", "hi": "बांबिल", "kn": "ಬೊಂಬಿಲ", "ml": "ബോംബ്", "en": "Bombay Duck", "kok": "बोंबिल"}',
 'Harpadon nehereus', 'Synodontidae',
 '{"sst_range": [26, 29], "depth_range": [5, 50]}',
 '{"gujarat": ["Jun-Dec"], "maharashtra": ["Jun-Nov"]}',
 '["gujarat", "maharashtra"]'),

('sardine',
 '{"mr": "तारली", "gu": "sardin", "hi": "सार्डीन", "kn": "ಭೂತಾಯಿ", "ml": "മത്തി", "en": "Indian Sardine", "kok": "ताएरलो"}',
 'Sardinella longiceps', 'Clupeidae',
 '{"sst_range": [27, 30], "depth_range": [5, 80], "chlorophyll_min": 0.8}',
 '{"karnataka": ["Jun-Nov"], "kerala": ["Year-round, peak Jun-Nov"]}',
 '["karnataka", "kerala", "goa"]'),

('seer_surmai',
 '{"mr": "सुरमई", "gu": "surmai", "hi": "सुरमई", "kn": "ಈಸ್ ‍Ware", "ml": "നെയ്‌മ‌ín", "en": "Seer Fish (Surmai)", "kok": "सुरमयो"}',
 'Scomberomorus commerson', 'Scombridae',
 '{"sst_range": [25, 29], "depth_range": [30, 300]}',
 '{"all": ["Year-round, peak Oct-Apr"]}',
 '["gujarat", "maharashtra", "goa", "karnataka", "kerala"]');

-- ==============================================
-- MARINE PROTECTED AREAS (Sample)
-- ==============================================
INSERT INTO marine_protected_areas (name, state, polygon, protection_level, rules)
VALUES
('Gulf of Kachchh Marine National Park',
 'gujarat',
 ST_Multi(ST_GeomFromText('POLYGON((68.5 22.2, 69.5 22.2, 69.5 22.8, 68.5 22.8, 68.5 22.2))', 4326)),
 'National Park',
 'No fishing, no anchoring, no waste disposal'),

('Malvan Marine Sanctuary',
 'maharashtra',
 ST_Multi(ST_GeomFromText('POLYGON((73.45 16.03, 73.55 16.03, 73.55 16.08, 73.45 16.08, 73.45 16.03))', 4326)),
 'Sanctuary',
 'Restricted fishing, no trawling, no coral collection'),

('Gahirmatha Marine Sanctuary',
 'karnataka',
 ST_Multi(ST_GeomFromText('POLYGON((74.1 14.1, 74.5 14.1, 74.5 14.4, 74.1 14.4, 74.1 14.1))', 4326)),
 'Sanctuary',
 'Restricted during olive ridley nesting (Nov-Apr)');
