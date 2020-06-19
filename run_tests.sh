#!/bin/bash

rc=0

# Make sure there is __init__.py in each dir containing python scripts
find backend tests -name '*.py' | xargs dirname | sort | uniq | xargs -I {} bash -c "test -f {}/__init__.py || ( echo {} directory does not have __init__.py! && false )"
rc=$(($rc+$?))

for testdir in backend tests
do
  echo -e "Checking sources in $testdir\n"

  # Run pylint
  echo -e "Running pylint\n"
  pylint --rcfile=./pylintrc $testdir --output-format=colorized
  rc=$(($rc+$?))

  # Run flake8
  echo -e "Running flake8\n"
  flake8 --append-config=setup.cfg $testdir
  rc=$(($rc+$?))
  echo ""
done

# Run pytest
pytest -v tests/
rc=$(($rc+$?))

exit $rc
