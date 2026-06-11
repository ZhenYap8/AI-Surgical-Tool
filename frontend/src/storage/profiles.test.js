import { afterEach, describe, expect, it } from "vitest";
import {
  loadProfiles,
  loadSelectedProfileId,
  saveProfiles,
  saveSelectedProfileId,
} from "./profiles";

const sampleProfile = {
  id: "1",
  name: "Dr. Smith",
  grade: "ST3",
  proceduresPerformed: 25,
  primaryProcedure: "Suturing",
  riskIndex: 5,
  skills: ["laparoscopy"],
  createdAt: 1,
  updatedAt: 1,
};

afterEach(() => {
  localStorage.clear();
});

describe("profile storage", () => {
  it("persists and reloads profiles", () => {
    saveProfiles([sampleProfile]);
    expect(loadProfiles()).toEqual([sampleProfile]);
  });

  it("filters invalid stored profiles", () => {
    saveProfiles([sampleProfile, { id: 2 }, { name: "No id" }]);
    expect(loadProfiles()).toEqual([sampleProfile]);
  });

  it("persists and reloads selected profile id", () => {
    saveProfiles([sampleProfile]);
    saveSelectedProfileId(sampleProfile.id);
    expect(loadSelectedProfileId(loadProfiles())).toBe(sampleProfile.id);
  });

  it("clears selected id when profile no longer exists", () => {
    saveSelectedProfileId("missing");
    expect(loadSelectedProfileId([])).toBe("");
  });
});
