import { z, defineCollection } from 'astro:content';

const storiesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    // מאפשר תאריך כטקסט או כתאריך, וממיר אותו אוטומטית לתאריך אמיתי
    date: z.string().or(z.date()).transform((val) => {
        const d = new Date(val);
        // בדיקה: האם התאריך יצא לא תקין?
        if (isNaN(d.getTime())) {
            // אופציונלי: הדפס לקונסול כדי שתדע שיש בעיה
            console.warn(`⚠️ Found invalid date: "${val}", using current date instead.`);
            return new Date(); // מחזיר את התאריך של היום כברירת מחדל
        }
        return d;
    }),
    author: z.string().default('לא ידוע'),
    categories: z.array(z.string()).optional(),
    tags: z.array(z.string()).optional(),
    // שדות נוספים שציינת שיש לך
    original_url: z.string().optional(),
  }),
});

export const collections = {
  'stories': storiesCollection,
};