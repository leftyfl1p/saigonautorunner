MODULES = jailed
include $(THEOS)/makefiles/common.mk

TWEAK_NAME = SaigonAutoRunner
DISPLAY_NAME = SaigonAutoRunner
BUNDLE_ID = com.leftyfl1p.saigonautorunner
PROFILE = com.leftyfl1p.saigonautorunner

SaigonAutoRunner_FILES = Tweak.xm
SaigonAutoRunner_IPA = ./Saigon.ipa

include $(THEOS_MAKE_PATH)/tweak.mk
