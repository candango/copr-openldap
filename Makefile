.PHONY: help lint spec-check build test clean

SPEC := openldap.spec

help:
	@printf '%s\n' \
	  'make spec-check  Validate the RPM spec syntax' \
	  'make build       Build the source RPM and binary RPMs locally' \
	  'make test        Run package validation tests' \
	  'make clean       Remove local build output'

spec-check:
	rpmspec -P $(SPEC) >/dev/null

build: spec-check
	@command -v rpmbuild >/dev/null || { echo 'rpmbuild is required'; exit 1; }
	rpmbuild -ba $(SPEC)

test:
	bash ./tests/validate-package.sh

clean:
	rm -rf BUILD BUILDROOT RPMS SRPMS SOURCES SPECS
