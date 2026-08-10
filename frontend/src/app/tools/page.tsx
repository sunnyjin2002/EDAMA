"use client";

import { useState, useMemo } from "react";

interface ToolEntry {
  name: string;
  category: "Official" | "Community";
  tags?: string[];
  description: string;
  link: string;
}

interface Section {
  id: string;
  title: string;
  tools: ToolEntry[];
}

// tags as constants, to prevent misspellings.
const tag_ax: string = "anti-xeno"
const tag_bgs: string = "BGS"
const tag_col: string = "colonization"
const tag_combat: string = "combat"
const tag_explore: string = "exploration"
const tag_mining: string = "mining"
const tag_ship: string = "ship builds"
const tag_trade: string = "trade"
const tag_pp: string = "powerplay"

const sections: Section[] = [
  {
    id: "databases",
    title: "Databases",
    tools: [
      {
        name: "INARA",
        category: "Community",
        description:
          "Comprehensive database — markets, outfitting, engineers, fleet tracking, squadrons, and more.",
        link: "https://inara.cz/elite/",
        tags: [],
      },
      {
        name: "EDSM (Elite Dangerous Star Map)",
        category: "Community",
        description:
          "Galactic mapping project with exploration data, celestial body search, and flight logs.",
        link: "https://www.edsm.net/",
        tags: [tag_explore],
      },
      {
        name: "Elite:Dangerous Astrometrics",
        category: "Community",
        description:
          "Elite: Dangerous Astrometrics is a website devoted to providing maps, graphs, charts, and data extracted from the Elite: Dangerous game.",
        link: "https://edastro.com/",
        tags: [tag_explore],
      },
      {
        name: "Elite:Dangerous Codex",
        category: "Community",
        description:
          "Providing a complete overview of all available third party tools, interesting threads, community websites/wikis and videos.",
        link: "https://edastro.com/",
        tags: [],
      },
      {
        name: "Spansh",
        category: "Community",
        description:
          "Route plotting, trade data, neutron highway planner, and fleet carrier analytics.",
        link: "https://www.spansh.co.uk/",
        tags: [tag_explore],
      },
    ],
  },
  {
    id: "tools",
    title: "Tools",
    tools: [
      {
        name: "Coriolis",
        category: "Community",
        description:
          "Ship build planner — experiment with loadouts, compare stats, and share configurations.",
        link: "https://coriolis.io/",
        tags: [tag_ship],
      },
      {
        name: "ED Merit Miner",
        category: "Community",
        description:
          "A tool to help you find the best prices for mining & earning merits for your powerplay faction.",
        link: "https://meritminer.cc/",
        tags: [tag_mining, tag_pp],
      },
      {
        name: "EDMining",
        category: "Community",
        description:
          "An updated guide and location resource for mining in Elite Dangerous.",
        link: "https://edmining.com/",
        tags: [tag_mining],
      },
      {
        name: "EDSY",
        category: "Community",
        description:
          "Detailed ship builder with in-depth engineering calculations, heat modeling, and power analysis.",
        link: "https://edsy.org/",
        tags: [tag_combat],
      },
      {
        name: "Elite BGS",
        category: "Community",
        description:
          "Detailed ship builder with in-depth engineering calculations, heat modeling, and power analysis.",
        link: "https://elitebgs.app/",
        tags: [tag_bgs],
      },
      {
        name: "Elite:Dangerous Tools Collection",
        category: "Community",
        description:
          "A collection of tools and guides for: mining, distance calculation, road to riches, massacre.",
        link: "https://edsy.org/",
        tags: [tag_combat,tag_mining,tag_trade],
      },
      {
        name: "MetaElite",
        category: "Community",
        description:
          "MetaElite is a role playing environment that allows the ED community to create interactive story telling for the community, closely integrated into your ED gameplay.",
        link: "https://raxxla.org/",
        tags: [tag_explore],
      },
      {
        name: "Powerplay Assistant",
        category: "Community",
        description:
          "A web app to help CMDRs with Powerplay 2.0 activities.",
        link: "https://elite.niceygy.net/",
        tags: [tag_pp],
      },
      {
        name: "Raven Colonial",
        category: "Community",
        description:
          "Fleet carrier jump planner and coordination tool for carrier owners and hitchhikers.",
        link: "https://ravencolonial.com",
        tags: [tag_col],
      },
      {
        name: "Wanderer's Toolbox",
        category: "Community",
        description:
          "",
        link: "https://wanderer-toolbox.com/",
        tags: [],
      },
    ],
  },
  {
    id: "guides",
    title: "Guides",
    tools: [
      {
        name: "Anti-Xeno Wiki",
        category: "Community",
        description:
          "The primary repository for the Anti-Xeno Initiative, here you will find tutorials, guides and detailed breakdowns of Thargoid Combat and Thargoids in Elite: Dangerous.",
        link: "https://wiki.antixenoinitiative.com/en/home",
        tags: [tag_ax],
      },
      {
        name: "Sirius Corporation Covert Creations (SCCC)",
        category: "Community",
        description:
          "Hosts a set of utilities. TO COMPLETE THIS DESCRIPTION.",
        link: "https://siriuscorp.cc/",
        tags: [tag_combat, tag_ship],
      },
    ],
  },
  {
    id: "forums",
    title: "Elite Forums",
    tools: [
      {
        name: "Elite Dangerous Forums",
        category: "Official",
        description: "The official Frontier forums for Elite Dangerous.",
        link: "https://forums.frontier.co.uk/categories/elite-dangerous/",
        tags: [],
      },
      {
        name: "INARA Discuss",
        category: "Community",
        description: "INARA-hosted discussion boards covering news, gameplay, and community events.",
        link: "https://inara.cz/elite/board/",
        tags: [],
      },
      {
        name: "r/EliteDangerous",
        category: "Community",
        description: "Main Elite Dangerous subreddit — news, screenshots, discussion, and community highlights.",
        link: "https://www.reddit.com/r/EliteDangerous/",
        tags: [],
      },
      {
        name: "r/EliteExplorers",
        category: "Community",
        description: "Exploration-focused subreddit — expedition logs, discovery screenshots, and route tips.",
        link: "https://www.reddit.com/r/eliteexplorers/",
        tags: [tag_explore],
      },
      {
        name: "r/EliteExobiology",
        category: "Community",
        description: "Exobiology and organic data — genus hunting strategies, value tables, and findings.",
        link: "https://www.reddit.com/r/EliteExobiology/",
        tags: [tag_explore],
      },
    ],
  },
  {
    id: "organizations",
    title: "Organizations",
    tools: [
      {
        name: "Anti-Xeno Initiative (AXI)",
        category: "Community",
        description: "A player community dedicated to protecting humanity from the Thargoid threat.",
        link: "https://antixenoinitiative.com/",
        tags: [tag_combat,tag_ax],
      },
      {
        name: "Fuel Rats",
        category: "Community",
        description: "A player-organized service for providing fuel to CMDRs that run out of fuel on accident, and thus stranded in space.",
        link: "https://fuelrats.com/",
        tags: [tag_explore],
      },
      {
        name: "Hull Seals",
        category: "Community",
        description: "A player-organized service dedicated to Hull Repairs, Broken Canopy rescues, or SRV strandings.",
        link: "https://hullseals.space/",
        tags: [tag_explore],
      },
      {
        name: "New Pilots Initiative",
        category: "Community",
        description: "A squadron that provides support infrastructure for newly qualified pilots, helping them to head out into the galaxy and develop into their chosen career.",
        link: "https://newp.io/",
        tags: [tag_ship],
      },
      {
        name: "Pilots Trade Network(PTN)",
        category: "Community",
        description: "We Exist to Make You Rich.",
        link: "https://pilotstradenetwork.com/",
        tags: [tag_trade],
      },
    ],
  },
  {
    id: "lore",
    title: "Lore and Information Archive",
    tools: [
      {
        name: "Canonn Research",
        category: "Community",
        description: "An independent cooperative made up of thousands of Commanders committed to science and discovering the mysteries of the universe.",
        link: "https://canonn.science",
        tags: [tag_explore,"lore"],
      },
      {
        name: "Élite Dangereuse",
        category: "Community",
        description: "The Élite Dangereuse offers interactive narrative adventures in the heart of the galaxy.",
        link: "https://elitedangereuse.com/en/index.php",
        tags: [tag_explore],
      },
      {
        name: "Elite Dangerous Wiki",
        category: "Official",
        description: "Fandom wiki covering ships, factions, lore, engineers, and game mechanics.",
        link: "https://elite-dangerous.fandom.com/wiki/Elite_Dangerous_Wiki",
        tags: ["lore"],
      },
      {
        name: "EDDN (Elite Dangerous Data Network)",
        category: "Community",
        description:
          "Real-time data relay network — trade prices, star system scans, and outfitting data used by tools like INARA and EDSM.",
        link: "https://eddn.edcd.io/",
        tags: [tag_explore],
      },
      {
        name: "edGGG",
        category: "Community",
        description: "CMDR Arcanic's comprehensive catalog for the game's rarest wonders - the Green Gas Giants.",
        link: "https://ed-ggg.github.io/edggg/",
        tags: [tag_explore],
      },
    ],
  },
  {
    id: "music",
    title: "Music Albums & Composers for Elite",
    tools: [
      {
        name: "ToCoSo",
        category: "Community",
        description: "CMDR ToCoSo's songs, inspired by Elite Dangerous.",
        link: "https://tocoso.bandcamp.com/",
        tags: [],
      },
    ],
  },
  {
    id: "others",
    title: "Other Websites, for Fun Only",
    tools: [
      {
        name: "Park My Spaceship",
        category: "Community",
        description: "A 3rd party website, that allows one to place a spaceship (from many games and fictions) in a real place on Earth. The website has the anaconda available.",
        link: "https://parkmyspaceship.com",
        tags: [],
      },
    ],
  },
];

const ALL_TAGS = [...new Set(sections.flatMap((s) => s.tools.flatMap((t) => t.tags ?? [])))].sort();

function ToolsTable({ data }: { data: ToolEntry[] }) {
  return (
    <div className="bg-ed-panel border border-ed-border rounded-lg overflow-hidden mb-8">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b border-ed-border">
            <th className="p-3 w-44">Name</th>
           <th className="p-3 w-36">Official / Community</th>
            <th className="p-3 w-36">Tags</th>
            <th className="p-3 hidden md:table-cell">Description</th>
            <th className="p-3 w-36">Link</th>
          </tr>
        </thead>
        <tbody>
          {data.map((tool) => (
            <tr key={tool.name} className="border-b border-ed-border/50">
              <td className="p-3 text-white font-medium align-top">{tool.name}</td>
              <td className="p-3">
                <span
                  className={`inline-block px-2 py-0.5 text-xs rounded border ${
                    tool.category === "Official"
                      ? "bg-green-900/30 text-green-300 border-green-700"
                      : "bg-blue-900/30 text-blue-300 border-blue-700"
                  }`}
                >
                  {tool.category}
                </span>
              </td>
              <td className="p-3 align-top">
                <div className="flex flex-wrap gap-1">
                  {(tool.tags ?? []).map((tag) => (
                    <span
                      key={tag}
                      className="inline-block px-1.5 py-0.5 text-xs rounded bg-ed-orange/10 text-ed-orange border border-ed-orange/30"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </td>
              <td className="p-3 text-gray-400 hidden md:table-cell align-top">{tool.description}</td>
              <td className="p-3 align-top">
                <a
                  href={tool.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-ed-orange hover:underline"
                >
                  Visit &rarr;
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ToolsPage() {
  const [query, setQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());

  const filteredSections = useMemo(() => {
    const hasFilters = query.trim() !== "" || selectedTags.size > 0;
    return sections.map((section) => {
      const filtered = section.tools.filter((tool) => {
        const matchesQuery =
          !query.trim() ||
          tool.name.toLowerCase().includes(query.toLowerCase()) ||
          tool.description.toLowerCase().includes(query.toLowerCase());
        const matchesTags =
          selectedTags.size === 0 ||
          (tool.tags ?? []).some((tag) => selectedTags.has(tag));
        return matchesQuery && matchesTags;
      });
      return { ...section, tools: filtered };
    }).filter((section) => {
      if (!hasFilters && section.tools.length === 0) return true;
      return section.tools.length > 0;
    });
  }, [query, selectedTags]);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  };

  return (
    <div className="flex gap-8">
      {/* Sidebar */}
      <aside className="hidden lg:block w-52 shrink-0">
        <nav className="sticky top-6">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Sections
          </h2>
          <ul className="space-y-1">
            {sections.map((section) => (
              <li key={section.id}>
                <a
                  href={`#${section.id}`}
                  className="block px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-ed-panel rounded transition-colors"
                >
                  {section.title}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h1 className="text-2xl font-bold text-white mb-2">Tools and Guides</h1>
        <p className="text-gray-400 mb-8">
          A curated collection of official and community-built tools,
          databases, and guides for Elite Dangerous.
        </p>

        {/* Search and tag filters */}
        <div className="mb-6 space-y-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Find your desired guide or tool..."
            className="w-full max-w-md px-3 py-2 bg-ed-panel border border-ed-border rounded text-white text-sm focus:outline-none focus:border-ed-orange"
          />
          <div className="flex flex-wrap gap-1.5">
            {ALL_TAGS.map((tag) => {
              const active = selectedTags.has(tag);
              return (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`inline-block px-2 py-1 text-xs rounded border transition-colors ${
                    active
                      ? "bg-ed-orange/20 text-ed-orange border-ed-orange/50"
                      : "bg-ed-panel text-gray-500 border-ed-border hover:text-gray-300 hover:border-gray-600"
                  }`}
                >
                  {tag}
                </button>
              );
            })}
            {selectedTags.size > 0 && (
              <button
                onClick={() => setSelectedTags(new Set())}
                className="px-2 py-1 text-xs text-gray-500 hover:text-white transition-colors"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {filteredSections.map((section) => (
          <section key={section.id} id={section.id} className="scroll-mt-6">
            <h2 className="text-lg font-semibold text-white mb-3">
              {section.title}
            </h2>
            {section.tools.length > 0 ? (
              <ToolsTable data={section.tools} />
            ) : (
              <div className="bg-ed-panel border border-ed-border border-dashed rounded-lg p-6 mb-8 text-center">
                <p className="text-gray-600 text-sm">Coming soon</p>
              </div>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}
