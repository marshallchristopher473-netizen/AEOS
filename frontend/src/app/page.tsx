import { redirect } from 'next/navigation';

import { DEFAULT_SIGNED_IN_PATH } from '@/lib/auth/redirect';

export default function HomePage() {
  redirect(DEFAULT_SIGNED_IN_PATH);
}
