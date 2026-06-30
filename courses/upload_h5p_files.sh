#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   1. Put all generated .h5p files into ./_incoming_h5p/
#   2. Run: bash courses/upload_h5p_files.sh
#   3. Run: git add courses && git commit -m "Add JEMIX Academy H5P lessons" && git push

SRC_DIR="_incoming_h5p"

copy_lesson() {
  local src="$1"
  local dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -f "$SRC_DIR/$src" ]]; then
    cp "$SRC_DIR/$src" "$dst"
    echo "OK: $dst"
  else
    echo "MISSING: $SRC_DIR/$src" >&2
  fi
}

copy_lesson "JEMIX_Academy_Module_01_Lesson_1_1_H5Pcom.h5p" "courses/module1/1_1/lesson.h5p"
copy_lesson "JEMIX_Academy_1_2_Gde_primenyayutsya_nasosy.h5p" "courses/module1/1_2/lesson.h5p"
copy_lesson "JEMIX_Academy_1_3_Istoriya_nasosov.h5p" "courses/module1/1_3/lesson.h5p"
copy_lesson "JEMIX_Academy_1_4_Osnovnye_vidy_nasosov.h5p" "courses/module1/1_4/lesson.h5p"
copy_lesson "JEMIX_Academy_1_5_Assortiment_JEMIX.h5p" "courses/module1/1_5/lesson.h5p"
copy_lesson "JEMIX_Academy_Module_1_Final_Test.h5p" "courses/module1/final_test/lesson.h5p"

copy_lesson "JEMIX_Academy_2_1_Davlenie_rashod_napor.h5p" "courses/module2/2_1/lesson.h5p"
copy_lesson "JEMIX_Academy_2_2_Poteri_napora.h5p" "courses/module2/2_2/lesson.h5p"
copy_lesson "JEMIX_Academy_2_3_Rabochaya_tochka_nasosa.h5p" "courses/module2/2_3/lesson.h5p"
copy_lesson "JEMIX_Academy_2_4_Kavitaciya_i_vysota_vsasyvaniya.h5p" "courses/module2/2_4/lesson.h5p"
copy_lesson "JEMIX_Academy_2_5_Itogovy_raschetny_keys.h5p" "courses/module2/2_5/lesson.h5p"

copy_lesson "JEMIX_Academy_3_1_Karta_assortimenta_JEMIX.h5p" "courses/module3/3_1/lesson.h5p"
copy_lesson "JEMIX_Academy_3_2_Avtomaticheskie_nasosnye_stancii.h5p" "courses/module3/3_2/lesson.h5p"
copy_lesson "JEMIX_Academy_3_3_Poverhnostnye_nasosy.h5p" "courses/module3/3_3/lesson.h5p"
copy_lesson "JEMIX_Academy_3_4_Skvazhinnye_nasosy.h5p" "courses/module3/3_4/lesson.h5p"
copy_lesson "JEMIX_Academy_3_5_1_Kolodeznye_nasosy_Osnovy.h5p" "courses/module3/3_5_1/lesson.h5p"
copy_lesson "JEMIX_Academy_3_5_2_Kolodeznye_nasosy_Podbor_i_praktika.h5p" "courses/module3/3_5_2/lesson.h5p"
copy_lesson "JEMIX_Academy_3_6_1_Drenazhnye_nasosy_Osnovy.h5p" "courses/module3/3_6_1/lesson.h5p"
