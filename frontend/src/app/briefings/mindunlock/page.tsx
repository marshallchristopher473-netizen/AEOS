import { redirect } from 'next/navigation';
import { MINDUNLOCK_BRIEFING } from '@/content/mindunlock';

export default function MindUnlockIndex() {
  redirect(`/briefings/${MINDUNLOCK_BRIEFING.slug}/${MINDUNLOCK_BRIEFING.sections[0].slug}`);
}
