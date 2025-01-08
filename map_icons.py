from enum import IntEnum, Enum

class IconType(IntEnum):
    # Bases and Defenses
    FORWARD_BASE_1 = 8
    HOSPITAL = 11
    VEHICLE_FACTORY = 12
    REFINERY = 17
    SHIPYARD = 18
    TECH_CENTER = 19  # Engineering Center in Update 37
    
    # Resource Fields
    SALVAGE_FIELD = 20
    COMPONENT_FIELD = 21
    FUEL_FIELD = 22
    SULFUR_FIELD = 23
    
    # Special Structures
    WORLD_MAP_TENT = 24
    TRAVEL_TENT = 25
    TRAINING_AREA = 26
    KEEP = 27
    OBSERVATION_TOWER = 28
    FORT = 29
    TROOP_SHIP = 30
    
    # Industry
    SULFUR_MINE = 32
    STORAGE_FACILITY = 33
    FACTORY = 34
    GARRISON_STATION = 35  # Safehouse
    ROCKET_SITE = 37
    SALVAGE_MINE = 38
    CONSTRUCTION_YARD = 39
    COMPONENT_MINE = 40
    
    # Major Structures
    RELIC_BASE_1 = 45
    RELIC_BASE_2 = 46
    RELIC_BASE_3 = 47
    MASS_PRODUCTION_FACTORY = 51
    SEAPORT = 52
    COASTAL_GUN = 53
    SOUL_FACTORY = 54
    TOWN_BASE_1 = 56
    TOWN_BASE_2 = 57
    TOWN_BASE_3 = 58
    
    # Special Weapons
    STORM_CANNON = 59
    INTEL_CENTER = 60
    
    # Resources
    COAL_FIELD = 61
    OIL_FIELD = 62
    
    # Rocket Facilities
    ROCKET_TARGET = 70
    ROCKET_GROUND_ZERO = 71
    ROCKET_SITE_WITH_ROCKET = 72
    FACILITY_MINE_OIL_RIG = 75
    
    # Latest Additions
    WEATHER_STATION = 83
    MORTAR_HOUSE = 84

class TeamID(Enum):
    NONE = "NONE"
    COLONIALS = "COLONIALS"
    WARDENS = "WARDENS"

# Team colors - slightly brighter but still dark
ICON_COLORS = {
    TeamID.COLONIALS: "#0F3F0F",  # Slightly brighter dark green
    TeamID.WARDENS: "#062850",    # Slightly brighter dark blue
}

# Structure specific colors
STRUCTURE_COLORS = {
    "ORANGE": "#8B4513",      # Saddle brown
    "BRIGHT_ORANGE": "#CC5500", # Darker bright orange (previously regular orange)
    "YELLOW": "#FFD700",
    "DARK_GREY": "#404040"
}

# Icon paths for different structures
ICON_PATHS = {
    IconType.FORWARD_BASE_1: "mapicons/MapIconForwardBase1.TGA",
    IconType.HOSPITAL: "mapicons/MapIconMedical.TGA",
    IconType.VEHICLE_FACTORY: "mapicons/MapIconVehicle.TGA",
    IconType.REFINERY: "mapicons/MapIconManufacturing.TGA",
    IconType.SHIPYARD: "mapicons/MapIconShipyard.TGA",
    IconType.TECH_CENTER: "mapicons/MapIconTechCenter.TGA",
    IconType.SALVAGE_FIELD: "mapicons/MapIconSalvage.TGA",
    IconType.COMPONENT_FIELD: "mapicons/MapIconComponents.TGA",
    IconType.FUEL_FIELD: "mapicons/MapIconFuel.TGA",
    IconType.SULFUR_FIELD: "mapicons/MapIconSulfur.TGA",
    IconType.WORLD_MAP_TENT: "mapicons/MapIconTownHall.TGA",
    IconType.TRAVEL_TENT: "mapicons/MapIconTownHall.TGA",
    IconType.TRAINING_AREA: "mapicons/MapIconWorkshop.TGA",
    IconType.KEEP: "mapicons/MapIconKeep.TGA",
    IconType.OBSERVATION_TOWER: "mapicons/MapIconObservationTower.TGA",
    IconType.FORT: "mapicons/MapIconFort.tga",
    IconType.TROOP_SHIP: "mapicons/MapIconTroopShip.tga",
    IconType.SULFUR_MINE: "mapicons/MapIconSulfurMine.TGA",
    IconType.STORAGE_FACILITY: "mapicons/MapIconStorageFacility.TGA",
    IconType.FACTORY: "mapicons/MapIconFactory.TGA",
    IconType.GARRISON_STATION: "mapicons/MapIconSafehouse.TGA",
    IconType.ROCKET_SITE: "mapicons/MapIconRocketSite.TGA",
    IconType.SALVAGE_MINE: "mapicons/MapIconSalvageMine.TGA",
    IconType.CONSTRUCTION_YARD: "mapicons/MapIconConstructionYard.TGA",
    IconType.COMPONENT_MINE: "mapicons/MapIconComponentMine.TGA",
    IconType.RELIC_BASE_1: "mapicons/MapIconRelicBase.TGA",
    IconType.RELIC_BASE_2: "mapicons/MapIconRelicBase.TGA",
    IconType.RELIC_BASE_3: "mapicons/MapIconRelicBase.TGA",
    IconType.MASS_PRODUCTION_FACTORY: "mapicons/MapIconMassProductionFactory.TGA",
    IconType.SEAPORT: "mapicons/MapIconSeaport.TGA",
    IconType.COASTAL_GUN: "mapicons/MapIconCoastalGun.TGA",
    IconType.SOUL_FACTORY: "mapicons/MapIconSoulFactory.TGA",
    IconType.TOWN_BASE_1: "mapicons/MapIconTownBaseTier1.TGA",
    IconType.TOWN_BASE_2: "mapicons/MapIconTownBaseTier1.TGA",
    IconType.TOWN_BASE_3: "mapicons/MapIconTownBaseTier1.TGA",
    IconType.STORM_CANNON: "mapicons/MapIconStormCannon.tga",
    IconType.INTEL_CENTER: "mapicons/MapIconIntelCenter.tga",
    IconType.COAL_FIELD: "mapicons/MapIconCoal.TGA",
    IconType.OIL_FIELD: "mapicons/MapIconOilWell.TGA",
    IconType.ROCKET_TARGET: "mapicons/MapIconRocketTarget.TGA",
    IconType.ROCKET_GROUND_ZERO: "mapicons/MapIconRocketGroundZero.TGA",
    IconType.ROCKET_SITE_WITH_ROCKET: "mapicons/MapIconRocketSiteWithRocket.TGA",
    IconType.FACILITY_MINE_OIL_RIG: "mapicons/MapIconFacilityMineOilRig.TGA",
    IconType.WEATHER_STATION: "mapicons/MapIconWeatherStation.TGA",
    IconType.MORTAR_HOUSE: "mapicons/MapIconMortarHouse.TGA"
}

# List of structures that should show team colors
TEAM_COLORED_STRUCTURES = {
    IconType.FORWARD_BASE_1,
    IconType.OBSERVATION_TOWER,
    IconType.FORT,
    IconType.TROOP_SHIP,
    IconType.REFINERY,
    IconType.FACTORY,
    IconType.CONSTRUCTION_YARD,
    IconType.MASS_PRODUCTION_FACTORY,
    IconType.TECH_CENTER,
    IconType.VEHICLE_FACTORY,
    IconType.SEAPORT,
    IconType.TOWN_BASE_1,
    IconType.TOWN_BASE_2,
    IconType.TOWN_BASE_3,
    IconType.RELIC_BASE_1,
    IconType.RELIC_BASE_2,
    IconType.RELIC_BASE_3,
    IconType.GARRISON_STATION,
    IconType.ROCKET_SITE,
    IconType.COASTAL_GUN,
    IconType.STORM_CANNON,
    IconType.MORTAR_HOUSE,
    IconType.INTEL_CENTER,
    IconType.OBSERVATION_TOWER,
    IconType.SHIPYARD,
    IconType.STORAGE_FACILITY,
    IconType.FACILITY_MINE_OIL_RIG,
    IconType.HOSPITAL,
    IconType.WEATHER_STATION
}

# Lists of structures with specific colors
ORANGE_COLORED_STRUCTURES = {
    IconType.SALVAGE_FIELD,
    IconType.SALVAGE_MINE,
}

BRIGHT_ORANGE_COLORED_STRUCTURES = {
    IconType.OIL_FIELD 
}

YELLOW_COLORED_STRUCTURES = {
    IconType.SULFUR_FIELD,
    IconType.SULFUR_MINE
}

GREY_COLORED_STRUCTURES = {
    IconType.COAL_FIELD
}

# Icon symbols (fallback if image not found)
ICON_SYMBOLS = {
    IconType.FORWARD_BASE_1: "🏠",
    IconType.HOSPITAL: "🏥",
    IconType.VEHICLE_FACTORY: "🚗",
    IconType.REFINERY: "⚒️",
    IconType.SHIPYARD: "🚢",
    IconType.TECH_CENTER: "🔬",
    IconType.SALVAGE_FIELD: "🔩",
    IconType.COMPONENT_FIELD: "🔧",
    IconType.FUEL_FIELD: "⛽",
    IconType.SULFUR_FIELD: "⚡",
    IconType.OBSERVATION_TOWER: "🗼",
    IconType.FORT: "🏰",
    IconType.TROOP_SHIP: "⛴️",
    IconType.STORAGE_FACILITY: "📦",
    IconType.FACTORY: "🏭",
    IconType.GARRISON_STATION: "🏠",
    IconType.ROCKET_SITE: "🚀",
    IconType.SALVAGE_MINE: "⛏️",
    IconType.CONSTRUCTION_YARD: "🏗️",
    IconType.COMPONENT_MINE: "⚙️",
    IconType.RELIC_BASE_1: "🏛️",
    IconType.RELIC_BASE_2: "🏛️",
    IconType.RELIC_BASE_3: "🏛️",
    IconType.MASS_PRODUCTION_FACTORY: "🏭",
    IconType.SEAPORT: "🚢",
    IconType.COASTAL_GUN: "💣",
    IconType.SOUL_FACTORY: "👻",
    IconType.TOWN_BASE_1: "🏰",
    IconType.TOWN_BASE_2: "🏰",
    IconType.TOWN_BASE_3: "🏰",
    IconType.STORM_CANNON: "💥",
    IconType.INTEL_CENTER: "📡",
    IconType.COAL_FIELD: "⚫",
    IconType.OIL_FIELD: "🛢️",
    IconType.ROCKET_TARGET: "🎯",
    IconType.ROCKET_GROUND_ZERO: "💥",
    IconType.WEATHER_STATION: "🌡️",
    IconType.MORTAR_HOUSE: "🎯"
}

# Range information for structures (in map units)
STRUCTURE_RANGES = {
    IconType.COASTAL_GUN: {
        'outer': 0.09,
        'inner': 0.07
    },
    IconType.STORM_CANNON: {
        'outer': 0.595,
        'inner': 0.460
    },
    IconType.GARRISON_STATION: 0.045,
    IconType.TOWN_BASE_1: 0.067,
    IconType.TOWN_BASE_2: 0.067,
    IconType.TOWN_BASE_3: 0.067,
    IconType.MORTAR_HOUSE: 0.05,
    IconType.RELIC_BASE_1: 0.063,
    IconType.RELIC_BASE_2: 0.063,
    IconType.RELIC_BASE_3: 0.063,
    IconType.OBSERVATION_TOWER: 0.11    
}
