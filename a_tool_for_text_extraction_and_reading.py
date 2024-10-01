# -*- coding: utf-8 -*-
"""A Tool for Text Extraction and Reading

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10tYJnHHkmn8EBVNPfGLkU63kpzyKsUvW
"""

# تثبيت المكتبات الأساسية
!pip install transformers
!pip install gradio
!pip install torch

pip install gTTS

import gradio as gr  # استدعاء المكتبات المطلوبة
from transformers import pipeline
from gtts import gTTS

# 1. إعداد نموذج تلخيص النصوص باللغة الإنجليزية
summarization_pipeline_en = pipeline("summarization", model="facebook/bart-large-cnn")

# 2. إعداد نموذج الترجمة من الإنجليزية إلى العربية
translation_pipeline = pipeline("translation_en_to_ar", model="Helsinki-NLP/opus-mt-en-ar")

# 3. دالة تلخيص النصوص باللغة الإنجليزية
def summarize_text_en(text):
    summary = summarization_pipeline_en(text, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)[0]["summary_text"]
    return summary

# 4. تحويل النص إلى صوت باستخدام gTTS
def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    audio_path = f"summary_audio_{lang_code}.mp3"
    tts.save(audio_path)
    return audio_path

# 5. دالة معالجة النصوص بناءً على اللغة المختارة
def process_text(text, language_option):
    if language_option == "English":
        # تلخيص النص باللغة الإنجليزية
        summary_en = summarize_text_en(text)
        # تحويل النص الملخص باللغة الإنجليزية إلى صوت
        audio_file_en = text_to_speech(summary_en, 'en')
        return summary_en, audio_file_en, None, None

    elif language_option == "English to Arabic":
        # تلخيص النص باللغة الإنجليزية
        summary_en = summarize_text_en(text)
        # ترجمة الملخص إلى العربية
        summary_ar = translation_pipeline(summary_en)[0]["translation_text"]
        # تحويل النص الملخص باللغة العربية إلى صوت
        audio_file_ar = text_to_speech(summary_ar, 'ar')
        return None, None, summary_ar, audio_file_ar

# 6. دالة استخراج النص من الملف الصوتي
def extract_text_from_audio(audio, audio_language):
    if audio_language == "Arabic":
        # استخدام نموذج wav2vec2 لاستخراج النصوص العربية
        asr_pipeline = pipeline("automatic-speech-recognition", model="jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
        text = asr_pipeline(audio)["text"]
    else:  # Assume English by default
        asr_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base")
        text = asr_pipeline(audio)["text"]
    return text

# 7. دالة تحديث المخرجات بناءً على اللغة المختارة
def update_outputs(language_option):
    if language_option == "English":
        return [gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)]
    elif language_option == "English to Arabic":
        return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)]

# 8. إنشاء واجهة Gradio مع تبويبين
with gr.Blocks() as iface:

    gr.Markdown("### A Tool for Text Extraction and Reading")

    with gr.Tab("Text Summarization & Speech"):
        with gr.Row():
            with gr.Column(scale=1):  # الجانب الأيسر (المدخلات)
                text_input = gr.Textbox(label="Enter Text")
                language_option = gr.Radio(["English", "English to Arabic"], label="Choose Summary Language")
                summarize_btn = gr.Button("Summarize")

                # إضافة الأمثلة للنصوص
                examples = ['''Project management is the process of planning, executing, and closing projects effectively and efficiently.
It involves coordinating resources, managing timelines, and ensuring that project objectives are met within scope and budget.
Successful project management is essential across various industries, including construction, IT, healthcare, and more.''']

                # استخدام gr.Examples لعرض الأمثلة
                gr.Examples(examples=examples, inputs=text_input)

            with gr.Column(scale=1):  # الجانب الأيمن (المخرجات)
                english_summary = gr.Textbox(label="English Summary", visible=False)
                english_audio = gr.Audio(label="English Summary Audio", type="filepath", visible=False)
                arabic_summary = gr.Textbox(label="Translated Arabic Summary", visible=False)
                arabic_audio = gr.Audio(label="Arabic Summary Audio", type="filepath", visible=False)

        # إظهار المخرجات المناسبة بناءً على اللغة المختارة
        language_option.change(
            update_outputs,
            inputs=language_option,
            outputs=[english_summary, english_audio, arabic_summary, arabic_audio]
        )

        # تشغيل عملية التلخيص والنطق
        summarize_btn.click(
            process_text,
            inputs=[text_input, language_option],
            outputs=[english_summary, english_audio, arabic_summary, arabic_audio]
        )

    with gr.Tab("Audio Transcription"):
        with gr.Row():
            with gr.Column(scale=1):  # الجانب الأيسر (المدخلات)
                audio_input = gr.Audio(label="Upload Audio", type="filepath")
                audio_language = gr.Radio(["Arabic", "English"], label="Audio Language")
                transcribe_btn = gr.Button("Transcribe Audio")

                # إضافة الأمثلة للأصوات
                audio_examples = [
                    "https://github.com/faisalaldwaish/test/raw/main/summary_audio_en%20(1).mp3",
                    "https://github.com/faisalaldwaish/test/raw/main/summary_audio_ar.mp3"
                ]
                # استخدام gr.Examples لعرض الأمثلة
                gr.Examples(examples=audio_examples, inputs=audio_input)

            with gr.Column(scale=1):  # الجانب الأيمن (المخرجات)
                transcribed_text = gr.Textbox(label="Transcribed Text")

        # تشغيل عملية استخراج النص من الصوت
        transcribe_btn.click(
            extract_text_from_audio,
            inputs=[audio_input, audio_language],
            outputs=[transcribed_text]
        )

# 9. تشغيل الواجهة
iface.launch()