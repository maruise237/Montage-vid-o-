// Données de démo pour le tournage : un formateur qui remplit sa masterclass via ses réseaux sociaux.
// Personnes et numéros fictifs (démo), aucun n'est présenté comme un vrai client.
export * from '/home/user/kamforms/mobile/screenshots/fixtures.mjs'
import * as base from '/home/user/kamforms/mobile/screenshots/fixtures.mjs'
const ago = (min) => new Date(Date.now() - min * 60_000).toISOString()
const TITRE = 'Masterclass : vendre sur TikTok'
const champs = [
  { id: 'nom', type: 'text', label: 'Nom complet', required: true },
  { id: 'tel', type: 'phone', label: 'Téléphone WhatsApp', required: true },
  { id: 'ville', type: 'text', label: 'Ville', required: true },
  { id: 'niveau', type: 'radio', label: 'Ton niveau', required: true, options: ['Je débute', "J'ai déjà vendu en ligne", 'Je vends chaque semaine'] },
  { id: 'session', type: 'radio', label: 'Session', required: true, options: ['Samedi 10 h', 'Dimanche 16 h'] },
]
const gens = [
  ['Grâce Nkolo', '+237 691 24 58 03', 'Yaoundé', 'Je débute', 'Samedi 10 h', 1],
  ['Koffi Mensah', '+225 07 48 21 65 90', 'Abidjan', "J'ai déjà vendu en ligne", 'Dimanche 16 h', 6],
  ['Aïcha Ndiaye', '+221 77 512 40 18', 'Dakar', 'Je débute', 'Samedi 10 h', 14],
  ['Brice Tchoupo', '+237 677 80 13 42', 'Douala', 'Je vends chaque semaine', 'Samedi 10 h', 31],
  ['Sandrine Mvondo', '+237 655 07 92 61', 'Douala', 'Je débute', 'Dimanche 16 h', 58],
  ['Yves Ondoa', '+241 66 30 75 12', 'Libreville', "J'ai déjà vendu en ligne", 'Samedi 10 h', 97],
]
export const submissions = gens.map(([nom, tel, ville, niveau, session, min], i) => ({
  id: `s${i + 1}`, formId: 'f1', createdAt: ago(min), data: { nom, tel, ville, niveau, session },
}))
export const inbox = submissions.map(s => ({ ...s, form: { title: TITRE } }))
export const forms = [
  { id: 'f1', title: TITRE, slug: 'masterclass-tiktok', active: true, createdAt: ago(2000), notificationsEnabled: true, lastSubmissionAt: ago(1), _count: { submissions: 37 } },
  ...base.forms.filter(f => f.id === 'f3'),
]
export const formDetail = {
  ...base.formDetail, title: TITRE, description: 'Samedi 10 h ou dimanche 16 h, en ligne. Places limitées.', slug: 'masterclass-tiktok',
  schema: { fields: champs }, submissionCount: 37, ending: { message: 'Inscription reçue ! Je t’écris sur WhatsApp.', confetti: true },
}
export const generated = { schema: { fields: champs.map((c, i) => ({ ...c, id: `g${i + 1}` })) } }
export const imported = { title: TITRE, schema: generated.schema, theme: { customColor: '#1f7a4d', bgColor: '#f1f8f4' }, ending: { message: 'Merci !' }, skipped: [] }
