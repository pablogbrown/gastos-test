/**
 * One-time script: signs bearer JWTs for all test users defined in auth/users.json
 * and writes them to auth/bearer-tokens.json.
 *
 * Setup (run from inside <e2e_dir> — see nybo-e2e-explore's Path Layout):
 *   cp auth/users.json.example auth/users.json
 *   # edit auth/users.json with your project's test users and roles
 *
 * Run:
 *   AUTH_SECRET=<your-secret> npx tsx generate-tokens.mts
 *
 * Note: if your app requires tokens to be registered in the database, do that
 * separately in your project after this script generates the JWTs.
 */
import { randomUUID } from 'crypto';
import { SignJWT } from 'jose';
import * as fs from 'fs';
import * as path from 'path';

interface UserConfig {
  role: string;
  userId: string;
  email: string;
  scopes: string[];
}

interface UsersConfig {
  secretEnvVar?: string;
  expiresInDays?: number;
  users: UserConfig[];
}

function loadUsersConfig(): UsersConfig {
  const configPath = path.join(process.cwd(), 'auth', 'users.json');
  if (!fs.existsSync(configPath)) {
    throw new Error(
      'auth/users.json not found.\n' +
      'Copy auth/users.json.example to auth/users.json and fill in your test users.'
    );
  }
  return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
}

function getTokenSecret(envVarName: string): Uint8Array {
  const secret = process.env[envVarName];
  if (!secret) throw new Error(`Missing secret: set the ${envVarName} environment variable`);
  return new TextEncoder().encode(secret);
}

async function main() {
  const config = loadUsersConfig();
  const secretEnvVar = config.secretEnvVar ?? 'AUTH_SECRET';
  const expiresInDays = config.expiresInDays ?? 90;
  const secret = getTokenSecret(secretEnvVar);

  const output: Record<string, string> = {};

  for (const u of config.users) {
    const jti = randomUUID();
    const expiresAt = new Date(Date.now() + expiresInDays * 24 * 60 * 60 * 1000);

    const jwt = await new SignJWT({ typ: 'api', email: u.email, scopes: u.scopes })
      .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
      .setSubject(u.userId)
      .setJti(jti)
      .setIssuedAt()
      .setExpirationTime(Math.floor(expiresAt.getTime() / 1000))
      .sign(secret);

    output[u.role] = jwt;
    console.log(`✓ ${u.role} (${u.email}) -> expires ${expiresAt.toISOString().split('T')[0]}`);
  }

  const outDir = path.join(process.cwd(), 'auth');
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, 'bearer-tokens.json'), JSON.stringify(output, null, 2));
  console.log('\nWritten: auth/bearer-tokens.json');
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
