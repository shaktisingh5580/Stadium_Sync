/**
 * ============================================================================
 * File: frontend/src/lib/firebase-client.ts
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/** Firebase browser authentication and App Check bridge.
 *
 * Public Firebase configuration is supplied at build time. Privileged service
 * account credentials remain exclusively in Cloud Run's runtime identity.
 */

interface FirebaseUser {
  getIdToken(forceRefresh?: boolean): Promise<string>;
}

interface FirebaseAuth {
  currentUser: FirebaseUser | null;
  signInWithCustomToken(token: string): Promise<unknown>;
}

interface FirebaseAppCheck {
  activate(siteKey: string, options: { isTokenAutoRefreshEnabled: boolean }): void;
  getToken(forceRefresh?: boolean): Promise<{ token: string }>;
}

interface FirebaseApp {
  auth(): FirebaseAuth;
  appCheck(): FirebaseAppCheck;
}

interface FirebaseCompat {
  apps: unknown[];
  initializeApp(config: Record<string, string>): FirebaseApp;
  app(): FirebaseApp;
}

declare global {
  interface Window {
    firebase?: FirebaseCompat;
  }
}

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

let appCheckActivated = false;

function getFirebaseApp(): FirebaseApp | null {
  const firebase = window.firebase;
  if (!firebase || !firebaseConfig.apiKey || !firebaseConfig.projectId) return null;
  const app = firebase.apps.length > 0 ? firebase.app() : firebase.initializeApp(firebaseConfig);

  const siteKey = import.meta.env.VITE_RECAPTCHA_ENTERPRISE_SITE_KEY;
  if (siteKey && !appCheckActivated) {
    app.appCheck().activate(siteKey, { isTokenAutoRefreshEnabled: true });
    appCheckActivated = true;
  }
  return app;
}

export async function signInWithFirebaseCustomToken(customToken: string): Promise<string> {
  const app = getFirebaseApp();
  if (!app) throw new Error('Firebase client configuration is incomplete');
  await app.auth().signInWithCustomToken(customToken);
  const user = app.auth().currentUser;
  if (!user) throw new Error('Firebase session was not created');
  const idToken = await user.getIdToken();
  sessionStorage.setItem('stadium_sync_token', idToken);
  sessionStorage.setItem('stadium_sync_auth_provider', 'firebase');
  return idToken;
}

export async function getAuthenticatedHeaders(): Promise<Record<string, string>> {
  const app = getFirebaseApp();
  if (!app || sessionStorage.getItem('stadium_sync_auth_provider') !== 'firebase') {
    const localToken = sessionStorage.getItem('stadium_sync_token');
    return localToken ? { Authorization: `Bearer ${localToken}` } : {};
  }

  const user = app.auth().currentUser;
  if (!user) return {};
  const headers: Record<string, string> = {
    Authorization: `Bearer ${await user.getIdToken()}`,
  };
  if (import.meta.env.VITE_RECAPTCHA_ENTERPRISE_SITE_KEY) {
    headers['X-Firebase-AppCheck'] = (await app.appCheck().getToken()).token;
  }
  return headers;
}

export function clearAuthenticatedSession(): void {
  sessionStorage.removeItem('stadium_sync_token');
  sessionStorage.removeItem('stadium_sync_auth_provider');
}
