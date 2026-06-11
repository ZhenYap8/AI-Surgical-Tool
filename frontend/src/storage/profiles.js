const PROFILES_KEY = "surgeon_profiles";
const SELECTED_PROFILE_KEY = "selected_surgeon_profile_id";

function isValidProfile(profile) {
  return (
    profile &&
    typeof profile === "object" &&
    typeof profile.id === "string" &&
    typeof profile.name === "string" &&
    profile.name.trim().length > 0
  );
}

export function loadProfiles() {
  try {
    const raw = localStorage.getItem(PROFILES_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed.filter(isValidProfile);
  } catch {
    return [];
  }
}

export function saveProfiles(profiles) {
  try {
    localStorage.setItem(PROFILES_KEY, JSON.stringify(profiles));
  } catch {
    // Ignore quota / private browsing errors
  }
}

export function loadSelectedProfileId(profiles) {
  try {
    const id = localStorage.getItem(SELECTED_PROFILE_KEY);
    if (!id) return "";
    return profiles.some((profile) => profile.id === id) ? id : "";
  } catch {
    return "";
  }
}

export function saveSelectedProfileId(id) {
  try {
    if (id) {
      localStorage.setItem(SELECTED_PROFILE_KEY, id);
    } else {
      localStorage.removeItem(SELECTED_PROFILE_KEY);
    }
  } catch {
    // Ignore quota / private browsing errors
  }
}
