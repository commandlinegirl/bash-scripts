#!/bin/bash

find . -type f -name "*.php" -exec sed -i .back -e 's/^<?php.*/<?php/g' {} \;
