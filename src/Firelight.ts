/**
 * @author MsEvildoom <msEvildoom@gmail.com>
 * @fileoverview Parses the .json content files from Book of Hours into a user-friendly readable format.
 * @copyright Firelight is an independent work by MsEvildoom and is not affiliated with Weather Factory Ltd, Secret Histories or any related official content. It is published under Weather Factory’s Sixth History Community Licence.
 *  The author has attempted to create a work that does not contain any of Weather Factory's writing; all content in Firelight must be provided by the user.
 *  Firelight by MsEvildoom is licensed under CC BY-NC 4.0, except any content owned by Weather Factory. 
 */


/**
 * The file structure of BOH content.
 */
const files: [string, string[]][] = [
    // Folders that aren't game content have been commented out
    // ['achievements', []],
    // ['cultures', []],
    ['decks', [
        'catalogue_decks.json',
        'challenges.json',
        'chats.json',
        'gathering_decks.json',
        'incidents_decks.json',]],
    // ['dicta', []],
    ['elements', [
        'abilities.json',
        'abilities2.json',
        'abilities3.json',
        'abilities4.json',
        'abilities_setup.json',
        'aspecteditems.json',
        'aspects_nx.json',
        'assistance.json',
        'celestial.json',
        'challenge_opportunities.json',
        'circumstances.json',
        'comforts.json',
        'contamination_aspects.json',
        'correspondence _addresses.json',
        'correspondence_elements.json',
        'credits.json',
        'incidents_n.json',
        'incidents_weather.json',
        'journal.json',
        'misc.json',
        'ns.json',
        'precursors.json',
        'resources.json',
        'skills.json',
        'skills_r.json',
        'tips_hints.json',
        'tlg.json',
        'tomes.json',
        'uncats.json',
        'visitors.json',
        'visitors_embarking.json',
        'visitors_other.json',
        'xlessons.json',
        'xlessons_unique.json',
        '_aspects.json',
        '_aspects_salons.json',
        '_debug.json',
        '_evolutionaspects.json',
        '_groupaspects.json',
        '_order_aspects.json',
        '_prototypes.json',
        '_resolutionaspects.json',
        '_visitactedaspects.json',
        '_visitaspects.json',
        '_visitreadaspects.json']],
    ['endings', [
        '_.json',
        '_u.json',]],
    ['legacies', [
        'bh_legacies.json']],
    ['recipes', [
        '0_consider_decontaminations.json',
        '1_consider_books.json',
        '2a_consider_open.json',
        '2b_consider_generic.json',
        '2c_consider_resolve.json',
        'beasts.json',
        'bookbinding.json',
        'celestial_recipes_time.json',
        'celestial_recipes_weather.json',
        'correspondence.json',
        'correspondence_ordering.json',
        'crafting_0_numina.json',
        'crafting_0_rest.json',
        'crafting_1_chandlery.json',
        'crafting_1_evolutions.json',
        'crafting_1_simplemanipulations.json',
        'crafting_2_keeper.json',
        'crafting_3_scholar.json',
        'crafting_4b_prentice.json',
        'gathering_1_exceptional.json',
        'gathering_2_seasonal.json',
        'other_activities.json',
        'renounce.json',
        'talk_1_visitors.json',
        'talk_2_visitors_payments_tutoring.json',
        'talk_3a_visitors_intercepts.json',
        'talk_3b_visitors_cantread.json',
        'talk_4a_visitors_intros.json',
        'talk_4b_visitors_specific_incidents.json',
        'talk_5z_visitors_fallthrough_hints.json',
        'talk_5_visitors_generic_consultations.json',
        'talk_6_assistance.json',
        'terrain.json',
        'understanding_1_numa.json',
        'understanding_2_upskill.json',
        'village.json',
        'visitors_correspondence_auctions.json',
        'wisdom_commitments.json',
        'wisdom_commitments_exotic.json',
        'z_fallthrough_hints.json',
        'z_fallthrough_placeholders.json',
        '_backstops.json',
        '_collections.json',
        '_endings_0_histories_present.json',
        '_endings_0_histories_unusual_present_record.json',
        '_endings_1_histories_record.json',
        '_endings_2_determinations.json',
        '_histories_hints.json',
        '_legacy.json',
        '_legacy_crafting_4a_prenticeplus_ambittable_unfriendly.json',
        '_legacy_crafting_obsolete.json',
        '_recipes.txt',
        '_startup_recipes.json',
        '__debug.json',]],
    // ['settings', []],
    ['verbs', [
        'celestial.json',
        'incidents.json',
        'librarian.json',
        'workstations_beds.json',
        'workstations_gathering.json',
        'workstations_legacy.json',
        'workstations_library_world.json',
        'workstations_unusual.json',
        'workstations_village.json',]]
];

const fileChecklist = document.getElementById('file-checklists');

if (fileChecklist) {
    for (const [folderName, fileNames] of files) {
        const folderElement = document.createElement('div');
        fileChecklist.append(folderElement);

        const folderNameElement = document.createElement('p');
        folderNameElement.textContent = folderName;
        const filesList = document.createElement('ul')

        folderElement.append(folderNameElement, filesList);

        for (const fileName of fileNames) {
            const fileElement = document.createElement('li');
            fileElement.textContent = fileName;
            fileElement.id = `${folderName}/${fileName}`
            filesList.append(fileElement)
        }
    }
} else {
    console.error('Could not find file-checklists')
}




const fileSelector = document.getElementById('file-selector');

if (fileSelector instanceof HTMLInputElement) {
    fileSelector.addEventListener('change', handleUpload);
} else {
    console.error('file-selector is not a input element')
}

/**
 * Verifies the uploaded files and sends them to the JSON parser
 * @param ev an HTMLInputElement being changed to upload files.
 */
function handleUpload(ev: Event): void {
    const inputElement = ev.currentTarget as HTMLInputElement;
    const fileList = inputElement.files;
    if (fileList) {
        console.log(fileList);
        if (fileList.length === 1) {
            const file = fileList.item(0);
            if (file) {
                if (file.name.toLowerCase().endsWith('.json')) {
                    parseJSON(file);
                } else { console.error("Uploaded file is not .json") }
            } else { console.error('Somehow the uploaded file is Null') }
        } else { console.error("Iteration hasn't been implemented yet") }
    } else { console.error('Somehow the uploaded FileList is Null.') }
}

function parseJSON(file: File) {
    const jsonText = file.text();
    const readJSON = jsonText.then((text) => {
        console.log(text)
        JSON.parse(text)
    }).then()

}




