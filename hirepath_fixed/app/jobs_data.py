from __future__ import annotations

from copy import deepcopy
from urllib.parse import quote_plus


def build_source_search_url(source: str, title: str, company: str, location: str) -> str:
    query = quote_plus(f"{title} {company}")
    location_q = quote_plus(location)
    source_key = source.lower()
    if source_key == "linkedin":
        return f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location_q}"
    if source_key == "indeed":
        return f"https://www.indeed.com/jobs?q={query}&l={location_q}"
    if source_key == "handshake":
        return f"https://www.google.com/search?q={quote_plus(f'site:joinhandshake.com/jobs {title} {company} {location}') }"
    return f"https://www.google.com/search?q={quote_plus(f'{source} {title} {company} {location}') }"


def build_recruiter_search_url(source: str, company: str, title: str, location: str) -> str:
    query = quote_plus(f"{company} recruiter OR talent acquisition OR hiring manager {title} {location}")
    source_key = source.lower()
    if source_key == "linkedin":
        return f"https://www.linkedin.com/search/results/people/?keywords={query}"
    return f"https://www.google.com/search?q={query}"


def build_linkedin_people_search(company: str, person_name: str) -> str:
    return f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(f'{person_name} {company} recruiter')}"


COMPANY_CONTACTS: dict[str, list[dict[str, str]]] = {
    "Harbor Goods": [
        {"name": "Maya Patel", "title": "Senior Talent Acquisition Partner", "team": "Talent Acquisition", "email": "maya.patel@harborgoods.example", "note": "Handles supply chain leadership hiring and campus referrals."},
        {"name": "Jordan Lee", "title": "HR Business Partner", "team": "People Operations", "email": "jordan.lee@harborgoods.example", "note": "Good contact for relocation, compensation bands, and internal team fit."},
        {"name": "Elena Ruiz", "title": "Recruiting Coordinator", "team": "Recruiting Operations", "email": "elena.ruiz@harborgoods.example", "note": "Useful for application status, interview scheduling, and process questions."},
    ],
    "Metro Commerce": [
        {"name": "Tina Brooks", "title": "Director of Talent", "team": "Talent Acquisition", "email": "tina.brooks@metrocommerce.example", "note": "Leads operations and distribution leadership recruiting."},
        {"name": "Samir Shah", "title": "People Operations Manager", "team": "HR", "email": "samir.shah@metrocommerce.example", "note": "Can advise on remote policy and team structure."},
        {"name": "Alicia Gomez", "title": "Senior Recruiter", "team": "Recruiting", "email": "alicia.gomez@metrocommerce.example", "note": "Strong outreach contact after tailoring your resume for the role."},
    ],
    "Northline Warehousing": [
        {"name": "Chris Walker", "title": "Campus Recruiter", "team": "University Recruiting", "email": "chris.walker@northlinewarehousing.example", "note": "Best first contact for internship and rotational openings."},
        {"name": "Priya Raman", "title": "HR Generalist", "team": "HR", "email": "priya.raman@northlinewarehousing.example", "note": "Can help with site-specific questions and shift expectations."},
        {"name": "Leo Martinez", "title": "Recruiting Operations Specialist", "team": "Talent Acquisition", "email": "leo.martinez@northlinewarehousing.example", "note": "Useful for application timing and interview logistics."},
    ],
    "Portwise Logistics": [
        {"name": "Abby Chen", "title": "Talent Partner", "team": "Talent Acquisition", "email": "abby.chen@portwise.example", "note": "Primary recruiter for analyst and inventory planning roles."},
        {"name": "Marcus Bell", "title": "HR Manager", "team": "Human Resources", "email": "marcus.bell@portwise.example", "note": "Strong contact for growth path and promotion timing questions."},
    ],
    "Cascade Retail": [
        {"name": "Renee Clark", "title": "Recruiting Lead", "team": "Talent Acquisition", "email": "renee.clark@cascaderetail.example", "note": "Great contact for hiring demand and role prioritization."},
        {"name": "Tom Alvarez", "title": "People Partner", "team": "People Team", "email": "tom.alvarez@cascaderetail.example", "note": "Can advise on culture and stakeholder expectations."},
    ],
    "Acme Freight": [
        {"name": "Nadia Foster", "title": "Senior Recruiter", "team": "Talent Acquisition", "email": "nadia.foster@acmefreight.example", "note": "Best outreach contact for logistics and analyst hiring."},
        {"name": "Ian Cole", "title": "HRBP", "team": "People Operations", "email": "ian.cole@acmefreight.example", "note": "Helpful for comp bands and location flexibility."},
    ],
    "BluePeak Retail": [
        {"name": "Mei Lin", "title": "University Recruiting Manager", "team": "University Recruiting", "email": "mei.lin@bluepeakretail.example", "note": "Owns intern and early career programs."},
        {"name": "David Ross", "title": "Recruiting Coordinator", "team": "Recruiting Operations", "email": "david.ross@bluepeakretail.example", "note": "Can help you understand hiring timeline and application routing."},
    ],
    "Northstar Distribution": [
        {"name": "Sara Ahmed", "title": "Campus Recruiter", "team": "Campus Talent", "email": "sara.ahmed@northstardistribution.example", "note": "Strong point of contact for internship and analyst roles."},
        {"name": "Ben Ortiz", "title": "HR Specialist", "team": "HR", "email": "ben.ortiz@northstardistribution.example", "note": "Can clarify relocation and site-level expectations."},
    ],
    "Summit Manufacturing": [
        {"name": "Olivia Reed", "title": "Talent Acquisition Partner", "team": "Talent Acquisition", "email": "olivia.reed@summitmanufacturing.example", "note": "Recruits procurement and sourcing talent."},
        {"name": "Kevin Tran", "title": "People Operations Lead", "team": "People Ops", "email": "kevin.tran@summitmanufacturing.example", "note": "Good contact for team structure and hiring process questions."},
    ],
    "Vertex Foods": [
        {"name": "Hannah Kim", "title": "University Recruiting Partner", "team": "University Recruiting", "email": "hannah.kim@vertexfoods.example", "note": "Best for internship openings and rotational programs."},
        {"name": "Joel Price", "title": "HR Coordinator", "team": "HR", "email": "joel.price@vertexfoods.example", "note": "Can clarify sponsorship and relocation topics."},
    ],
    "Orbit Components": [
        {"name": "Nora James", "title": "Procurement Recruiter", "team": "Talent Acquisition", "email": "nora.james@orbitcomponents.example", "note": "Strong outreach contact after resume tailoring."},
        {"name": "Victor Diaz", "title": "People Operations Manager", "team": "People Operations", "email": "victor.diaz@orbitcomponents.example", "note": "Helpful for benefits and hybrid work questions."},
    ],
    "Allied Sourcing": [
        {"name": "Emily Scott", "title": "Recruiting Manager", "team": "Recruiting", "email": "emily.scott@alliedsourcing.example", "note": "Leads analyst hiring and supplier management screening."},
        {"name": "Grace Wu", "title": "HRBP", "team": "Human Resources", "email": "grace.wu@alliedsourcing.example", "note": "Useful for career path and leveling questions."},
    ],
    "Beacon Procurement": [
        {"name": "Jason Kim", "title": "Talent Acquisition Specialist", "team": "Talent Acquisition", "email": "jason.kim@beaconprocurement.example", "note": "Strong first point of contact for early-career sourcing roles."},
        {"name": "Molly Evans", "title": "People Coordinator", "team": "People Team", "email": "molly.evans@beaconprocurement.example", "note": "Can help with process timing and onsite expectations."},
    ],
    "Cobalt Distribution": [
        {"name": "Trevor Hall", "title": "Recruiting Partner", "team": "Talent Acquisition", "email": "trevor.hall@cobaltdistribution.example", "note": "Best for distribution and warehouse management roles."},
        {"name": "Lina Park", "title": "HR Manager", "team": "Human Resources", "email": "lina.park@cobaltdistribution.example", "note": "Can advise on site operations and team setup."},
    ],
    "Pioneer Fulfillment": [
        {"name": "Courtney Dean", "title": "Senior Recruiter", "team": "Recruiting", "email": "courtney.dean@pioneerfulfillment.example", "note": "Great contact for fulfillment leadership and analyst paths."},
        {"name": "Erik Lowe", "title": "HR Generalist", "team": "HR", "email": "erik.lowe@pioneerfulfillment.example", "note": "Can advise on shift expectations and advancement."},
    ],
}


BASE_JOBS: list[dict[str, object]] = [
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Supply Chain Manager", "company": "Harbor Goods", "location": "Seattle, WA", "salary_min": 92000, "salary_max": 115000, "salary_text": "$92k-$115k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Coordination", "Judgment and Decision Making", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Regional consumer goods operator building resilient replenishment and transportation planning workflows."},
    {"source": "Indeed", "role_slug": "supply-chain-manager", "title": "Distribution Operations Manager", "company": "Metro Commerce", "location": "Remote", "salary_min": 88000, "salary_max": 108000, "salary_text": "$88k-$108k", "employment_type": "full_time", "work_mode": "remote", "skills": ["Monitoring", "Time Management", "Microsoft Office software", "Role-specific keywords"], "company_blurb": "Fast-growing commerce network balancing distributed fulfillment operations and inventory visibility."},
    {"source": "Handshake", "role_slug": "supply-chain-manager", "title": "Inventory Control Supervisor", "company": "Northline Warehousing", "location": "Memphis, TN", "salary_min": 32, "salary_max": 38, "salary_text": "$32-$38/hr", "employment_type": "internship", "work_mode": "onsite", "skills": ["Active Listening", "Coordination", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Warehouse operator known for high-volume inbound and outbound inventory control."},
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Demand Planning Manager", "company": "Cascade Retail", "location": "Portland, OR", "salary_min": 98000, "salary_max": 122000, "salary_text": "$98k-$122k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Omnichannel retailer improving forecasting and store replenishment accuracy."},
    {"source": "Indeed", "role_slug": "supply-chain-manager", "title": "Warehouse Operations Manager", "company": "Cobalt Distribution", "location": "Columbus, OH", "salary_min": 86000, "salary_max": 101000, "salary_text": "$86k-$101k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Coordination", "Time Management", "Microsoft Office software", "Quantified achievement evidence"], "company_blurb": "Distribution specialist focused on SLA discipline and labor planning."},
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Fulfillment Manager", "company": "Pioneer Fulfillment", "location": "Phoenix, AZ", "salary_min": 90000, "salary_max": 110000, "salary_text": "$90k-$110k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Monitoring", "Coordination", "Time Management", "Role-specific keywords"], "company_blurb": "E-commerce fulfillment operator scaling multi-node shipment orchestration."},
    {"source": "Handshake", "role_slug": "supply-chain-manager", "title": "Operations Leadership Intern", "company": "Harbor Goods", "location": "Seattle, WA", "salary_min": 28, "salary_max": 34, "salary_text": "$28-$34/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Active Listening", "Coordination", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Early-career pathway into transportation, inventory, and site leadership tracks."},
    {"source": "Indeed", "role_slug": "supply-chain-manager", "title": "Transportation Planning Lead", "company": "Portwise Logistics", "location": "Savannah, GA", "salary_min": 82000, "salary_max": 96000, "salary_text": "$82k-$96k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Monitoring", "Critical Thinking", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Port-side logistics network connecting import schedules to inland distribution."},
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Inventory Planning Manager", "company": "BluePeak Retail", "location": "Remote", "salary_min": 93000, "salary_max": 114000, "salary_text": "$93k-$114k", "employment_type": "full_time", "work_mode": "remote", "skills": ["Judgment and Decision Making", "Monitoring", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Remote-first retail planning team coordinating inventory turns and in-stock performance."},
    {"source": "Handshake", "role_slug": "supply-chain-manager", "title": "Site Operations Supervisor", "company": "Northstar Distribution", "location": "Chicago, IL", "salary_min": 31, "salary_max": 37, "salary_text": "$31-$37/hr", "employment_type": "internship", "work_mode": "onsite", "skills": ["Coordination", "Time Management", "Microsoft Office software", "Role-specific keywords"], "company_blurb": "Midwest distribution site investing in future warehouse and planning leaders."},
    {"source": "Indeed", "role_slug": "supply-chain-manager", "title": "Procurement Operations Manager", "company": "Summit Manufacturing", "location": "Atlanta, GA", "salary_min": 95000, "salary_max": 118000, "salary_text": "$95k-$118k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Writing", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Manufacturing team improving supplier performance and operational execution."},
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Regional Logistics Manager", "company": "Acme Freight", "location": "Dallas, TX", "salary_min": 97000, "salary_max": 121000, "salary_text": "$97k-$121k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Coordination", "Judgment and Decision Making", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Freight operator with strong cross-functional leadership opportunities."},
    {"source": "Handshake", "role_slug": "supply-chain-manager", "title": "Inventory Leadership Fellow", "company": "Cascade Retail", "location": "Portland, OR", "salary_min": 29, "salary_max": 35, "salary_text": "$29-$35/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Active Listening", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Structured internship into planning, merchandising, and site operations."},
    {"source": "Indeed", "role_slug": "supply-chain-manager", "title": "Operations Excellence Manager", "company": "Metro Commerce", "location": "Austin, TX", "salary_min": 91000, "salary_max": 112000, "salary_text": "$91k-$112k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Time Management", "Microsoft Office software", "Quantified achievement evidence"], "company_blurb": "Cross-functional operations role centered on process standardization and KPI ownership."},
    {"source": "LinkedIn", "role_slug": "supply-chain-manager", "title": "Materials Flow Manager", "company": "Vertex Foods", "location": "Los Angeles, CA", "salary_min": 94000, "salary_max": 116000, "salary_text": "$94k-$116k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Coordination", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Food manufacturing network focused on inbound material and production flow reliability."},

    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Procurement Analyst", "company": "Summit Manufacturing", "location": "Atlanta, GA", "salary_min": 65000, "salary_max": 80000, "salary_text": "$65k-$80k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Negotiation", "Writing", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Manufacturing sourcing team optimizing supplier terms and spend analytics."},
    {"source": "Handshake", "role_slug": "procurement-analyst", "title": "Sourcing Intern", "company": "Vertex Foods", "location": "Los Angeles, CA", "salary_min": 24, "salary_max": 30, "salary_text": "$24-$30/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Negotiation", "Reading Comprehension", "Microsoft Office software", "Quantified achievement evidence"], "company_blurb": "Food sourcing internship with exposure to suppliers, cost tracking, and contract support."},
    {"source": "Indeed", "role_slug": "procurement-analyst", "title": "Purchasing Analyst", "company": "Orbit Components", "location": "Phoenix, AZ", "salary_min": 59000, "salary_max": 72000, "salary_text": "$59k-$72k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Critical Thinking", "Writing", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Component supplier balancing cost, lead time, and vendor quality metrics."},
    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Strategic Sourcing Analyst", "company": "Allied Sourcing", "location": "Chicago, IL", "salary_min": 69000, "salary_max": 84000, "salary_text": "$69k-$84k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Negotiation", "Critical Thinking", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Advisory-led sourcing group emphasizing supplier strategy and savings capture."},
    {"source": "Indeed", "role_slug": "procurement-analyst", "title": "Category Analyst", "company": "Beacon Procurement", "location": "Nashville, TN", "salary_min": 61000, "salary_max": 76000, "salary_text": "$61k-$76k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Writing", "Reading Comprehension", "Microsoft Office software", "Role-specific keywords"], "company_blurb": "Category team supporting spend analysis and vendor performance reviews."},
    {"source": "Handshake", "role_slug": "procurement-analyst", "title": "Supplier Management Intern", "company": "Harbor Goods", "location": "Seattle, WA", "salary_min": 26, "salary_max": 31, "salary_text": "$26-$31/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Negotiation", "Writing", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Internship rotating through supplier performance and sourcing dashboards."},
    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Spend Analytics Analyst", "company": "Metro Commerce", "location": "Remote", "salary_min": 67000, "salary_max": 83000, "salary_text": "$67k-$83k", "employment_type": "full_time", "work_mode": "remote", "skills": ["Critical Thinking", "Microsoft Excel", "Quantified achievement evidence", "Role-specific keywords"], "company_blurb": "Analytics-forward procurement team with a distributed operating model."},
    {"source": "Indeed", "role_slug": "procurement-analyst", "title": "Buyer Planner Analyst", "company": "Portwise Logistics", "location": "Savannah, GA", "salary_min": 63000, "salary_max": 77000, "salary_text": "$63k-$77k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Reading Comprehension", "Negotiation", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Planning and procurement role tied closely to port-driven demand cycles."},
    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Procurement Operations Analyst", "company": "Northstar Distribution", "location": "Chicago, IL", "salary_min": 64000, "salary_max": 79000, "salary_text": "$64k-$79k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Writing", "Critical Thinking", "Microsoft Office software", "Quantified achievement evidence"], "company_blurb": "Distribution procurement team looking for structured analysis and stakeholder support."},
    {"source": "Handshake", "role_slug": "procurement-analyst", "title": "Strategic Sourcing Fellow", "company": "BluePeak Retail", "location": "Remote", "salary_min": 25, "salary_max": 30, "salary_text": "$25-$30/hr", "employment_type": "internship", "work_mode": "remote", "skills": ["Negotiation", "Reading Comprehension", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Remote internship supporting supplier scorecards and RFP prep."},
    {"source": "Indeed", "role_slug": "procurement-analyst", "title": "Cost Analysis Buyer", "company": "Cobalt Distribution", "location": "Columbus, OH", "salary_min": 62000, "salary_max": 74000, "salary_text": "$62k-$74k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Critical Thinking", "Writing", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Operations-focused procurement role with spend control and supplier scorecards."},
    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Vendor Performance Analyst", "company": "Pioneer Fulfillment", "location": "Phoenix, AZ", "salary_min": 66000, "salary_max": 81000, "salary_text": "$66k-$81k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Negotiation", "Critical Thinking", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Fast-moving fulfillment environment with measurable vendor KPI ownership."},
    {"source": "Handshake", "role_slug": "procurement-analyst", "title": "Supply Base Analyst Intern", "company": "Orbit Components", "location": "Phoenix, AZ", "salary_min": 25, "salary_max": 29, "salary_text": "$25-$29/hr", "employment_type": "internship", "work_mode": "onsite", "skills": ["Reading Comprehension", "Writing", "Microsoft Office software", "Quantified achievement evidence"], "company_blurb": "Hands-on supplier support internship in a manufacturing environment."},
    {"source": "Indeed", "role_slug": "procurement-analyst", "title": "Procurement Reporting Analyst", "company": "Cascade Retail", "location": "Portland, OR", "salary_min": 65000, "salary_max": 78000, "salary_text": "$65k-$78k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Writing", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Retail procurement team focused on dashboards, supplier reporting, and savings tracking."},
    {"source": "LinkedIn", "role_slug": "procurement-analyst", "title": "Contracts & Sourcing Analyst", "company": "Harbor Goods", "location": "Seattle, WA", "salary_min": 68000, "salary_max": 85000, "salary_text": "$68k-$85k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Negotiation", "Writing", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Role blending contract support, supplier negotiations, and operational reporting."},

    {"source": "Handshake", "role_slug": "entry-level-supply-chain-analyst", "title": "Supply Chain Analyst Intern", "company": "Northstar Distribution", "location": "Chicago, IL", "salary_min": 24, "salary_max": 29, "salary_text": "$24-$29/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Critical Thinking", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Early-career analyst track with direct planning and reporting exposure."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Logistics Analyst", "company": "Acme Freight", "location": "Dallas, TX", "salary_min": 62000, "salary_max": 76000, "salary_text": "$62k-$76k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Systems Analysis", "Complex Problem Solving", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Analyst role tying route performance to transportation cost actions."},
    {"source": "Indeed", "role_slug": "entry-level-supply-chain-analyst", "title": "Inventory Analyst", "company": "BluePeak Retail", "location": "Remote", "salary_min": 26, "salary_max": 32, "salary_text": "$26-$32/hr", "employment_type": "internship", "work_mode": "remote", "skills": ["Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Remote inventory planning team focused on in-stock and turns analytics."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Demand Planning Analyst", "company": "Cascade Retail", "location": "Portland, OR", "salary_min": 64000, "salary_max": 79000, "salary_text": "$64k-$79k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Planning analyst position with strong forecasting and merchandising exposure."},
    {"source": "Indeed", "role_slug": "entry-level-supply-chain-analyst", "title": "Transportation Analyst", "company": "Portwise Logistics", "location": "Savannah, GA", "salary_min": 61000, "salary_max": 74000, "salary_text": "$61k-$74k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Systems Analysis", "Monitoring", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Analyst role on carrier performance, dispatch flow, and route optimization."},
    {"source": "Handshake", "role_slug": "entry-level-supply-chain-analyst", "title": "Operations Analyst Fellow", "company": "Harbor Goods", "location": "Seattle, WA", "salary_min": 25, "salary_max": 31, "salary_text": "$25-$31/hr", "employment_type": "internship", "work_mode": "hybrid", "skills": ["Critical Thinking", "Active Listening", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Internship for students ready to support supply planning and site reporting."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Network Planning Analyst", "company": "Metro Commerce", "location": "Remote", "salary_min": 66000, "salary_max": 82000, "salary_text": "$66k-$82k", "employment_type": "full_time", "work_mode": "remote", "skills": ["Systems Analysis", "Complex Problem Solving", "Microsoft Office software", "Role-specific keywords"], "company_blurb": "Distributed operations team optimizing node placement and transfer logic."},
    {"source": "Indeed", "role_slug": "entry-level-supply-chain-analyst", "title": "Inventory Planning Analyst", "company": "Northline Warehousing", "location": "Memphis, TN", "salary_min": 60000, "salary_max": 73000, "salary_text": "$60k-$73k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Monitoring", "Microsoft Excel", "Quantified achievement evidence", "Role-specific keywords"], "company_blurb": "Warehouse inventory team managing control towers and cycle count insights."},
    {"source": "Handshake", "role_slug": "entry-level-supply-chain-analyst", "title": "Demand & Supply Intern", "company": "Vertex Foods", "location": "Los Angeles, CA", "salary_min": 24, "salary_max": 30, "salary_text": "$24-$30/hr", "employment_type": "internship", "work_mode": "onsite", "skills": ["Monitoring", "Critical Thinking", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Food planning internship with demand balancing and production coordination."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Business Intelligence Analyst, Supply Chain", "company": "Northstar Distribution", "location": "Chicago, IL", "salary_min": 68000, "salary_max": 84000, "salary_text": "$68k-$84k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Systems Analysis", "Microsoft Excel", "Quantified achievement evidence", "Role-specific keywords"], "company_blurb": "BI-leaning analyst role focused on network performance dashboards and reporting."},
    {"source": "Indeed", "role_slug": "entry-level-supply-chain-analyst", "title": "Replenishment Analyst", "company": "Beacon Procurement", "location": "Nashville, TN", "salary_min": 63000, "salary_max": 77000, "salary_text": "$63k-$77k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Critical Thinking", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Cross-functional analyst role connecting procurement and store replenishment."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Supply Planning Analyst", "company": "Orbit Components", "location": "Phoenix, AZ", "salary_min": 65000, "salary_max": 80000, "salary_text": "$65k-$80k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Complex Problem Solving", "Monitoring", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Manufacturing planning analyst supporting MRP and supplier readiness."},
    {"source": "Handshake", "role_slug": "entry-level-supply-chain-analyst", "title": "Fulfillment Analytics Intern", "company": "Pioneer Fulfillment", "location": "Phoenix, AZ", "salary_min": 25, "salary_max": 30, "salary_text": "$25-$30/hr", "employment_type": "internship", "work_mode": "onsite", "skills": ["Active Listening", "Monitoring", "Microsoft Excel", "Role-specific keywords"], "company_blurb": "Internship pairing KPI tracking with daily execution support in a fulfillment center."},
    {"source": "Indeed", "role_slug": "entry-level-supply-chain-analyst", "title": "Materials Analyst", "company": "Summit Manufacturing", "location": "Atlanta, GA", "salary_min": 62000, "salary_max": 76000, "salary_text": "$62k-$76k", "employment_type": "full_time", "work_mode": "hybrid", "skills": ["Systems Analysis", "Critical Thinking", "Microsoft Office software", "Role-specific keywords"], "company_blurb": "Planner-facing analyst role tied to supplier schedules and material availability."},
    {"source": "LinkedIn", "role_slug": "entry-level-supply-chain-analyst", "title": "Supply Chain Reporting Analyst", "company": "Cobalt Distribution", "location": "Columbus, OH", "salary_min": 64000, "salary_max": 78000, "salary_text": "$64k-$78k", "employment_type": "full_time", "work_mode": "onsite", "skills": ["Monitoring", "Systems Analysis", "Microsoft Excel", "Quantified achievement evidence"], "company_blurb": "Reporting-heavy analyst role focused on distribution center performance and inventory turns."},
]


JOBS: list[dict[str, object]] = []
for raw_job in BASE_JOBS:
    job = deepcopy(raw_job)
    company = str(job["company"])
    title = str(job["title"])
    location = str(job["location"])
    source = str(job["source"])
    job["apply_url"] = build_source_search_url(source, title, company, location)
    job["recruiter_search_url"] = build_recruiter_search_url(source, company, title, location)
    contacts = []
    for contact in COMPANY_CONTACTS.get(company, []):
        contact_copy = deepcopy(contact)
        contact_copy["linkedin_url"] = build_linkedin_people_search(company, contact_copy["name"])
        contacts.append(contact_copy)
    job["recruiter_contacts"] = contacts
    JOBS.append(job)
