-- Create a small table that stores facts used by the RAG application.
CREATE TABLE IF NOT EXISTS company_facts (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fact TEXT NOT NULL UNIQUE
);

-- Clear old seed data so rerunning this file produces the same facts.
DELETE FROM company_facts;

-- Add dummy facts about the fictional company.
INSERT INTO company_facts (fact)
VALUES
    ('Lumen Bikes was founded in 2021 in Portland, Oregon.'),
    ('Lumen Bikes makes lightweight solar-assisted bicycles.'),
    ('Lumen Bikes offers free repairs for the first two years; after that, it charges $45 per repair appointment plus the cost of replacement parts.'),
    ('Lumen Bikes ships bicycles to customers in the United States and Canada.')
ON CONFLICT (fact) DO NOTHING;
