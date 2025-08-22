import streamlit as st
import json
import uuid
import base64
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Audio Annotation Tool",
    page_icon="🎙️",
    layout="wide"
)

# --- Initialize Session State ---
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}
if 'speakers' not in st.session_state:
    st.session_state.speakers = []
if 'segments' not in st.session_state:
    st.session_state.segments = []
if 'page_state' not in st.session_state:
    st.session_state.page_state = 'metadata_input'

# --- Helper Functions ---
def get_json_download_link(data, filename="annotated_data.json"):
    """Generates a link to download the annotated JSON data."""
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    return f'<a href="data:file/json;base64,{b64}" download="{filename}">Download JSON File</a>'

# =====================================================================================
# CUSTOM AUDIO PLAYER COMPONENT (Unchanged)
# =====================================================================================
def audio_player_component(audio_bytes: bytes):
    """
    Creates a custom audio player component using wavesurfer.js that displays
    the current time, allows click-to-seek, and has playback speed control.
    """
    b64_audio = base64.b64encode(audio_bytes).decode()
    component_html = f"""
    <div id="waveform-container" style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; width: 90%;">
        <div id="waveform"></div>
        <div style="margin-top: 15px; display: flex; align-items: center; gap: 20px;">
            <button id="playBtn" style="padding: 8px 16px; border-radius: 5px; border: 1px solid #ccc; cursor: pointer;">Play</button>
            <div style="font-family: monospace; font-size: 1.2em;">
                Current Time: <span id="time-display">0.000</span> s
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <label for="playbackSpeed">Speed:</label>
                <select id="playbackSpeed" style="border-radius: 5px; padding: 5px;">
                    <option value="0.5">0.5x</option>
                    <option value="1" selected>1.0x</option>
                    <option value="1.5">1.5x</option>
                    <option value="2">2.0x</option>
                </select>
            </div>
        </div>
    </div>
    <script src="https://unpkg.com/wavesurfer.js"></script>
    <script>
        var wavesurfer = WaveSurfer.create({{
            container: '#waveform',
            waveColor: 'violet',
            progressColor: 'purple',
            barWidth: 2,
            barRadius: 3,
            height: 100,
            barGap: 3,
            responsive: true,
            fillParent: true,
            minPxPerSec: 1,
            cursorWidth: 1,
            cursorColor: 'purple'
        }});
        wavesurfer.load('data:audio/wav;base64,{b64_audio}');

        const playBtn = document.getElementById('playBtn');
        const timeDisplay = document.getElementById('time-display');
        const speedSelector = document.getElementById('playbackSpeed');

        // Play/Pause button functionality
        playBtn.onclick = function() {{ wavesurfer.playPause(); }};

        // Update time display during playback
        wavesurfer.on('audioprocess', function() {{
            let currentTime = wavesurfer.getCurrentTime();
            timeDisplay.textContent = currentTime.toFixed(3);
        }});
        
        // Update time display on any interaction (click, drag, etc.) for immediate feedback
        wavesurfer.on('interaction', function() {{
            let currentTime = wavesurfer.getCurrentTime();
            timeDisplay.textContent = currentTime.toFixed(3);
        }});

        // Playback speed control
        speedSelector.onchange = function() {{
            wavesurfer.setPlaybackRate(this.value);
        }};
        
        // Update button text on play/pause/finish
        wavesurfer.on('finish', function () {{ playBtn.textContent = 'Play'; }});
        wavesurfer.on('play', function () {{ playBtn.textContent = 'Pause'; }});
        wavesurfer.on('pause', function () {{ playBtn.textContent = 'Play'; }});
    </script>
    """
    st.components.v1.html(component_html, height=200)


# =====================================================================================
# PAGE 1: METADATA INPUT FORM (Unchanged)
# =====================================================================================
def metadata_form():
    st.title("Step 1: Input Metadata")
    st.markdown("---")
    with st.form(key="metadata_form"):
        st.subheader("1. Type")
        type_name = st.text_input("Name", "MULTI SPEAKER LONG FORM TRANSCRIPTION")
        type_version = st.text_input("Version", "3.1")
        st.subheader("2. Language")
        lang_full = st.text_input("Full Language Name", "English (US)")
        lang_short = st.text_input("Short Name / Symbol", "en_US")
        st.subheader("3. Person in Audio")
        head_count = st.number_input("Head Count", min_value=1, value=1, step=1)
        st.subheader("4. Domain")
        domain_name = st.text_input("Domain Name", "Call-Center")
        topic_list = st.text_input("Topic List (comma-separated)", "Insurance, Claims")
        st.subheader("5. Annotator Info")
        annotator_id = st.text_input("Annotator ID", "e4fb5aa2")
        st.subheader("6. Convention Info")
        master_convention = st.text_input("Master Convention Name", "awsTranscriptionGuidelines_en_US_3.1")
        custom_addendum = st.text_input("Custom Addendum (Optional)")
        st.subheader("7. Speaker Details")
        speakers_input = []
        for i in range(int(head_count)):
            st.markdown(f"**Speaker {i+1}**")
            speaker_id = st.text_input(f"Speaker ID (leave blank for auto)", key=f"speaker_id_{i}")
            gender = st.selectbox(f"Gender", ["Female", "Male", "Other"], key=f"gender_{i}")
            gender_source = st.text_input(f"Gender Source", "Annotator", key=f"gender_source_{i}")
            speaker_nativity = st.selectbox(f"Speaker Nativity", ["Native", "Non-Native"], key=f"nativity_{i}")
            speaker_nativity_source = st.text_input(f"Speaker Nativity Source", "Annotator", key=f"nativity_source_{i}")
            speaker_role = st.text_input(f"Speaker Role", "Agent", key=f"role_{i}")
            speaker_role_source = st.text_input(f"Speaker Role Source", "Annotator", key=f"role_source_{i}")
            st.markdown(f"*Speaker Dominant Varieties*")
            language_locale = st.text_input(f"Language Locale", lang_short, key=f"lang_locale_{i}")
            language_variety = st.text_input(f"Language Variety (comma-separated)", key=f"lang_variety_{i}")
            other_language_influence = st.text_input(f"Other Language Influence (comma-separated)", key=f"other_lang_influence_{i}")
            speakers_input.append({
                "speakerId": speaker_id if speaker_id else str(uuid.uuid4()),
                "gender": gender, "genderSource": gender_source, "speakerNativity": speaker_nativity,
                "speakerNativitySource": speaker_nativity_source, "speakerRole": speaker_role,
                "speakerRoleSource": speaker_role_source,
                "speakerDominantVarieties": [{"languageLocale": language_locale, "languageVariety": [v.strip() for v in language_variety.split(",") if v.strip()], "otherLanguageInfluence": [v.strip() for v in other_language_influence.split(",") if v.strip()]}],
                "languages": [language_locale]
            })
        submit_button = st.form_submit_button(label="Save Metadata and Proceed to Annotation")
        if submit_button:
            st.session_state.metadata = {
                "type": {"name": type_name, "version": type_version},
                "languageInfo": {"spokenLanguages": [lang_full], "speakerDominantVarieties": [{"languageLocale": speakers_input[0]["speakerDominantVarieties"][0]["languageLocale"] if speakers_input else lang_short, "languageVariety": speakers_input[0]["speakerDominantVarieties"][0]["languageVariety"] if speakers_input else [], "otherLanguageInfluence": speakers_input[0]["speakerDominantVarieties"][0]["otherLanguageInfluence"] if speakers_input else []}]},
                "domainInfo": {"domainVersion": "1.0", "domainList": [{"domain": domain_name, "topicList": [t.strip() for t in topic_list.split(',')]}]},
                "annotatorInfo": {"annotatorId": annotator_id},
                "conventionInfo": {"masterConventionName": master_convention, "customAddendum": custom_addendum}
            }
            st.session_state.speakers = speakers_input
            st.session_state.page_state = 'annotation'
            st.success("Metadata saved successfully! Proceed to the annotation step below.")
            st.rerun()

# =====================================================================================
# PAGE 2: AUDIO ANNOTATION AND JSON EDITOR (MODIFIED)
# =====================================================================================
def annotation_page():
    st.title("Step 2: Audio Annotation")
    
    st.markdown("""
        <style>
        div[data-testid="stElementContainer"]:has(iframe[title^="st.iframe"]) {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("---")
    uploaded_file = st.file_uploader("Upload a .wav file", type=["wav"])

    if uploaded_file:
        audio_bytes = uploaded_file.getvalue()
        
        st.subheader("Audio Player")
        audio_player_component(audio_bytes)
        
        st.subheader("Add a New Segment")
        st.markdown("Use the player above to find start/end times, then enter the details below.")

        with st.form(key="segment_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.text_input("Start Time (seconds.milliseconds, e.g., 4.500)", "0.000")
            with col2:
                end_time = st.text_input("End Time (seconds.milliseconds, e.g., 8.250)", "5.000")

            primary_type = st.selectbox("Primary Type", ["Speech", "Noise", "Music", "Silence"], index=0)
            
            # --- CHANGE 1: UI elements are now always visible ---
            transcription = st.text_area("Transcription Content", "")
            loudness_level = st.selectbox("Loudness Level", ["Normal", "Quiet", "Loud"], index=0)

            # Ensure speakers exist before showing the dropdown
            if st.session_state.speakers:
                speaker_options = {s['speakerId']: f"Speaker {i+1} ({s.get('speakerRole', 'N/A')})" for i, s in enumerate(st.session_state.speakers)}
                selected_speaker_id = st.selectbox("Speaker", options=list(speaker_options.keys()), format_func=lambda x: speaker_options[x])
            else:
                st.warning("No speakers defined. Please add speakers in the metadata step.")
                selected_speaker_id = None

            add_segment_button = st.form_submit_button("Add Segment")

            # --- CHANGE 2: Data from all fields is now always added to the segment ---
            if add_segment_button:
                if selected_speaker_id is None:
                    st.error("Cannot add segment. Please define at least one speaker in the metadata.")
                else:
                    new_segment = {
                        "start": start_time,
                        "end": end_time,
                        "segmentId": str(uuid.uuid4()),
                        "primaryType": primary_type,
                        "loudnessLevel": loudness_level,
                        "language": st.session_state.metadata['languageInfo']['speakerDominantVarieties'][0]['languageLocale'],
                        "speakerId": selected_speaker_id,
                        "transcriptionData": {"content": transcription}
                    }
                    st.session_state.segments.append(new_segment)
                    st.success("Segment added successfully!")
                    st.rerun()

    if st.session_state.segments:
        st.subheader("Annotated Segments")
        st.markdown("You can delete segments here. For detailed edits, use the JSON editor below.")
        
        sorted_segments = sorted(st.session_state.segments, key=lambda x: float(x.get('start', 0)))
        st.session_state.segments = sorted_segments

        for i, seg in enumerate(st.session_state.segments[:]):
            with st.expander(f"Segment {i+1}: {seg['start']} - {seg['end']} ({seg['primaryType']})"):
                st.json(seg)
                if st.button("Delete Segment", key=f"del_{seg['segmentId']}"):
                    st.session_state.segments.pop(i)
                    st.rerun()

    if st.session_state.metadata and st.session_state.speakers:
        final_json = {
            "type": st.session_state.metadata['type'],
            "value": {
                "languages": [lang['languageLocale'] for lang in st.session_state.metadata['languageInfo']['speakerDominantVarieties']],
                "languageInfo": st.session_state.metadata['languageInfo'],
                "domainInfo": st.session_state.metadata['domainInfo'],
                "conventionInfo": st.session_state.metadata['conventionInfo'],
                "annotatorInfo": st.session_state.metadata['annotatorInfo'],
                "speakers": st.session_state.speakers,
                "segments": st.session_state.segments,
                "taskStatus": {"segmentation": {"workflowStatus": "COMPLETE", "workflowType": "LABEL"}, "speakerId": {"workflowStatus": "COMPLETE", "workflowType": "LABEL"}, "transcription": {"workflowStatus": "COMPLETE", "workflowType": "LABEL"}}
            }
        }
        st.subheader("Live JSON Editor")
        st.markdown("You can directly edit, update, or delete values in the JSON below. Click 'Apply Changes' to save them to the application state.")
        json_string = json.dumps(final_json, indent=4)
        edited_json_string = st.text_area(label="JSON Data", value=json_string, height=600, key="json_editor")
        col1, col2 = st.columns([1, 4])
        with col1:
            apply_button = st.button("Apply JSON Changes")
        if apply_button:
            try:
                edited_data = json.loads(edited_json_string)
                st.session_state.metadata['type'] = edited_data.get('type', st.session_state.metadata['type'])
                value_section = edited_data.get('value', {})
                st.session_state.metadata['languageInfo'] = value_section.get('languageInfo', st.session_state.metadata.get('languageInfo', {}))
                st.session_state.metadata['domainInfo'] = value_section.get('domainInfo', st.session_state.metadata.get('domainInfo', {}))
                st.session_state.metadata['conventionInfo'] = value_section.get('conventionInfo', st.session_state.metadata.get('conventionInfo', {}))
                st.session_state.metadata['annotatorInfo'] = value_section.get('annotatorInfo', st.session_state.metadata.get('annotatorInfo', {}))
                st.session_state.speakers = value_section.get('speakers', st.session_state.speakers)
                st.session_state.segments = value_section.get('segments', st.session_state.segments)
                st.success("JSON changes have been applied successfully!")
                st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format. Please correct the errors before applying. \n\nError details: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred while applying changes: {e}")
        st.subheader("Download Final Annotation")
        st.markdown(get_json_download_link(final_json, filename="annotated_data.json"), unsafe_allow_html=True)

# =====================================================================================
# MAIN APP ROUTER (Unchanged)
# =====================================================================================
if st.session_state.page_state == 'metadata_input':
    metadata_form()
elif st.session_state.page_state == 'annotation':
    if st.sidebar.button("⬅️ Back to Metadata"):
        st.session_state.page_state = 'metadata_input'
        st.rerun()
    annotation_page()

