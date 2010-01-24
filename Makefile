NAME=network_manager_gtk
LANGS= "en" "tr"

all:
	echo "make (tags | clean | pot | mo)"
tags:
	etags *.py $(NAME)/*.py
clean:
	find . -name "*~" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	find . -name "\#*" -exec rm  {} \;
pot:
	xgettext --keyword=_ -f "po/POTFILES.in" --output="po/$(NAME).pot"
mo:
	@for lang in $(LANGS);\
	do \
		mkdir -p locale/$$lang/LC_MESSAGES; \
		msgfmt --output-file=locale/$$lang/LC_MESSAGES/$(NAME).mo po/$$lang.po; \
	done
