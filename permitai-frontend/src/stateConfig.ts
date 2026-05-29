export interface StateConfiguration {
  id: string;
  name: string;
  hindiName: string;
  themeClass: string;
  authorityName: string;
  authorityAbbr: string;
  sealColor: string;
  helpline: string;
}

export const STATES_CONFIG: StateConfiguration[] = [
  {
    id: "karnataka",
    name: "Karnataka",
    hindiName: "कर्नाटक",
    themeClass: "state-theme-karnataka",
    authorityName: "Bruhat Bengaluru Mahanagara Palike",
    authorityAbbr: "BBMP",
    sealColor: "#f97316",
    helpline: "+91 80 2266 0000"
  },
  {
    id: "maharashtra",
    name: "Maharashtra",
    hindiName: "महाराष्ट्र",
    themeClass: "state-theme-maharashtra",
    authorityName: "Brihanmumbai Municipal Corporation",
    authorityAbbr: "BMC",
    sealColor: "#e11d48",
    helpline: "+91 22 2262 0251"
  },
  {
    id: "delhi",
    name: "Delhi",
    hindiName: "दिल्ली",
    themeClass: "state-theme-delhi",
    authorityName: "Municipal Corporation of Delhi",
    authorityAbbr: "MCD",
    sealColor: "#0d9488",
    helpline: "+91 11 2322 0010"
  },
  {
    id: "tamilnadu",
    name: "Tamil Nadu",
    hindiName: "तमिलनाडु",
    themeClass: "state-theme-tamilnadu",
    authorityName: "Greater Chennai Corporation",
    authorityAbbr: "GCC",
    sealColor: "#15803d",
    helpline: "+91 44 2530 3600"
  },
  {
    id: "telangana",
    name: "Telangana",
    hindiName: "तेलंगाना",
    themeClass: "state-theme-telangana",
    authorityName: "Greater Hyderabad Municipal Corporation",
    authorityAbbr: "GHMC",
    sealColor: "#db2777",
    helpline: "+91 40 2111 1111"
  }
];

export const getSelectedState = (): StateConfiguration => {
  const stored = localStorage.getItem("selected_state_id");
  if (stored) {
    const config = STATES_CONFIG.find(s => s.id === stored);
    if (config) return config;
  }
  return STATES_CONFIG[0]; // Default is Karnataka/BBMP
};

export const saveSelectedState = (stateId: string) => {
  localStorage.setItem("selected_state_id", stateId);
};
