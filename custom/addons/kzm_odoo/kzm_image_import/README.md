[![Build Status](https://travis-ci.com/karizmaconseil/karizma_tools.svg?branch=14.0
)](https://travis-ci.com/karizmaconseil/karizma_tools)
# `User Manual module kzm_image_import`

## With xmlrpc;

- ### To import images with xmlrpc is done in 2 ways
  - #### Import to a remote machine:
    - Select the import type (XML-RPC);
    - Enter the IP address/URL (with http or https) of your machine ex: 0.0.0.0:8080/https://karizma.cc
    - Enter the name of the database
    - Enter login and password
    - Choose the model to which you want to import
    - Choose the search field (only int and char are available)
    - Choose the field linked to the model to which you want to import images
    - Enter the folder path that contain the images
    - Enter the folder path in case there is an error
    - Check Block importation if you want to block importation of inexisting records
    - Click on import

  - #### Import on the same machine:
    - Select the import type (XML-RPC)
    - Hook the image on server to indicate to the system that you want to import on the same machine
    - Choose the model to which you want to import
    - Choose the search field (only int and char are available)
    - Choose the field linked to the model to which you want to import images
    - Enter the folder path that contain the images
    - Enter the folder path in case there is an error
    - Check Block importation if you want to block importation of inexisting records
    - Click on import

## With excel file;

- ### For importing images with an excel file:
  - Select import type (Excel file);
  - Choose the model to which you want to import;
  - Choose the field linked to the model to which you want to import images;
  - Choose the excel file containing images;
    - N.B: - The images can be links, paths to the images in the local, but above all the excel workbook must be composed of 2 columns,
      one for id, external id or name(ex: 9, name_article) and the other image(ex: /local/path/img.png, http://www.google.com/images)
  - Click on import, to import images;

## With google Drive;
  - Select import type Google Drive
  - Enter the google drive folder
  - Click on import

