import profileData from "../../../data/profile.json";

export interface Profile {
  name: string;
  headline: string;
  bio: string;
  location: string;
  image: string;
  email: string | null;
  worksFor: string | null;
  sameAs: string[];
}

export const profile = profileData as Profile;
