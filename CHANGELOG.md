# Changelog

<!-- insertion marker -->
## [v1.4.55.3](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.55.3) - 2023-06-21

<small>[Compare with v1.4.55.2](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.55.2...v1.4.55.3)</small>

### Removed

- removed logmessage for index debugging ([e66be0a](https://github.com/dblevin1/docassemble-webapp/commit/e66be0a0b2c4e0b4190a285f9bee154d5df41111) by Daniel Blevins).

## [v1.4.55.2](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.55.2) - 2023-06-06

<small>[Compare with v1.4.55.1](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.55.1...v1.4.55.2)</small>

### Added

- add log message to index for debugging ([3170162](https://github.com/dblevin1/docassemble-webapp/commit/31701624f8f3d4e875ac72fc3f5baeebf694e1e3) by Daniel Blevins).

## [v1.4.55.1](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.55.1) - 2023-05-30

<small>[Compare with v1.4.52.3](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.52.3...v1.4.55.1)</small>

## [v1.4.52.3](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.52.3) - 2023-05-26

<small>[Compare with v](https://github.com/dblevin1/docassemble-webapp/compare/v...v1.4.52.3)</small>

### Removed

- remove background_action sleep ([72e6feb](https://github.com/dblevin1/docassemble-webapp/commit/72e6feb065a366063bf6d2d503fd5c5b55d7b8da) by Daniel Blevins).

## [v](https://github.com/dblevin1/docassemble-webapp/releases/tag/v) - 2023-05-19

<small>[Compare with v1.4.51.5](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.5...v)</small>

### Added

- add server init message ([a6bf6bf](https://github.com/dblevin1/docassemble-webapp/commit/a6bf6bfada77a27a24442c74ac4324610956a73d) by Daniel Blevins).

### Fixed

- fix bumpversion config ([36c6e48](https://github.com/dblevin1/docassemble-webapp/commit/36c6e48bb66090aff95ea02dfb79a28c1bc395b8) by Daniel Blevins).

## [v1.4.51.5](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.5) - 2023-05-14

<small>[Compare with v1.4.51.4](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.4...v1.4.51.5)</small>

## [v1.4.51.4](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.4) - 2023-05-13

<small>[Compare with v1.4.51.3](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.3...v1.4.51.4)</small>

## [v1.4.51.3](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.3) - 2023-05-13

<small>[Compare with first commit](https://github.com/dblevin1/docassemble-webapp/compare/6a25cb7db0fe630262f242150f23dd518956a3aa...v1.4.51.3)</small>

### Added

- add bumpversion release config ([f905399](https://github.com/dblevin1/docassemble-webapp/commit/f9053991b2fe150a28c34f398cab8a9a54a69b90) by Daniel Blevins).
- add available version badges to updatable packages ([c34935b](https://github.com/dblevin1/docassemble-webapp/commit/c34935bf0dd58d873f43ab772a02229f12bd8da4) by Daniel Blevins).
- add write_pip_conf ([6c9142c](https://github.com/dblevin1/docassemble-webapp/commit/6c9142c156d6fa8c0e919635bde3d03dc0a9548c) by Daniel Blevins).
- add identifier for this package ([3ea6d70](https://github.com/dblevin1/docassemble-webapp/commit/3ea6d7017f9f298b586c8a517b868e812b3e098b) by Daniel Blevins).
- add gitignore ([dfabe2d](https://github.com/dblevin1/docassemble-webapp/commit/dfabe2dc846cae0230d5c4b2413932fbd7210ccc) by Daniel Blevins).
- added all and any as jinja2 filters; fixed issue with validation messages of custom datatypes when used with show if ([35e6c25](https://github.com/dblevin1/docassemble-webapp/commit/35e6c254ae7bc827bffa807c0697cc48fc641e74) by Jonathan Pyle).
- additional pikepdf fixes ([4c540aa](https://github.com/dblevin1/docassemble-webapp/commit/4c540aa881d9ebaa7ea0cf1f3a1508ceed53e3d0) by Jonathan Pyle).
- Add error trace and log to context of custom error handlers ([3b87316](https://github.com/dblevin1/docassemble-webapp/commit/3b87316c5e6e53a62bca327b6fd7a023c51a17de) by Quinten Steenhuis).
- address autocomplete options; hidden input type; Configuration searching ([3ee3640](https://github.com/dblevin1/docassemble-webapp/commit/3ee364068b1a66426a72454e54267f40201f1dab) by Jonathan Pyle).
- added 'ip address ban enabled' Configuration directive; fixed translation on logout page; faster query for sessions to delete when deleting sessions using interview_list and a query or tag filtering; fix session_id parameter for resume_url; changed logrotate configuration to avoid error messages ([b028fdc](https://github.com/dblevin1/docassemble-webapp/commit/b028fdc069fc98f1611054dab474075c6164637e) by Jonathan Pyle).
- added the Configuration directive allow configuration editing and the Docker environment variable DAALLOWCONFIGURATIONEDITING to control whether the administrator can edit the Configuration; added Docker environment variables DADEBUG and DAENABLEPLAYGROUND; the allow updates and enable playground directives now affect access to API endpoints ([539a95b](https://github.com/dblevin1/docassemble-webapp/commit/539a95b6d351088d0792914775139c4b8433130f) by Jonathan Pyle).
- Added pip index url and pip extra index urls; added insertion_order option for .true_values(); allow API keys to be passed as bearer tokens; removed pathlib as a dependency; yesnoradio now sets variable to None if not required and not answered; fix issues with target_number's data type; update the exports of docassemble.base.legal so that they include everything exported by docassemble.base.util; issue with review blocks where set and follow up were not recognized if using the older syntax; issue with send_email() and send_sms() not processing DAList recipients; issue with navigation sections showing already-visited sections as not visited; fixed four-second timeout problem with error action. ([7c26c58](https://github.com/dblevin1/docassemble-webapp/commit/7c26c585f95633137c1ff880d2690afac9be9cec) by Jonathan Pyle).
- Add an explicit Schema.org item to the webpage ([d315142](https://github.com/dblevin1/docassemble-webapp/commit/d315142acecf01cf18d14f872ce66a83a3b51f46) by Bryce Willey).
- Add a aria-label to the progress bar ([2103763](https://github.com/dblevin1/docassemble-webapp/commit/2103763cc264caadc86a4c5f15e549c3dd310761) by Bryce Willey).
- Added optgroups to manual select fields, and to without 'fields' too ([dca27e3](https://github.com/dblevin1/docassemble-webapp/commit/dca27e3a68abf0223db1f6769ec71b927cd898fc) by Bryce Willey).
- Add provision for github PAT to install on server ([1f04f6a](https://github.com/dblevin1/docassemble-webapp/commit/1f04f6ab86148956c3594d9bac0579fb06d7a752) by plocket).
- address autocomplete trigger of change event; run preliminary assemble for checkin action ([355806c](https://github.com/dblevin1/docassemble-webapp/commit/355806c0240e99a36f735cbfcff182bfc13b089a) by Jonathan Pyle).
- added descriptive log messages to initialize.sh; added traceback to failure to assemble API error; changed the way the restart screen deals with ajax timeouts; avoided possibly duplicative install table add row command; fixed issue with None not appearing by default in tri-state input elements; fixed issue with code-generated checkbox fields where input was not accepted ([cda70a9](https://github.com/dblevin1/docassemble-webapp/commit/cda70a9ccedb10347a8d29be1326e67f2241e081) by Jonathan Pyle).
- additional on_failure and on_success options for DAWeb methods; random instance name for pdf_concatenate results; longer poll delay in package management UI ([486d37b](https://github.com/dblevin1/docassemble-webapp/commit/486d37b888ebc58c03e1684afa9801343614aea7) by Jonathan Pyle).
- added Jinja2 preprocessor feature; adjusted for ARM compatibility by disabling DAGoogleAPI's dependency; adjusted for xspace bug in new version of Pandoc; better removal of servers from supervisors list if they are non-responsive ([c3ecd3f](https://github.com/dblevin1/docassemble-webapp/commit/c3ecd3f37cbc27ed133c58f4420f245032ec2d0f) by Jonathan Pyle).
- additional input sanitizing for admin and developers ([621d49b](https://github.com/dblevin1/docassemble-webapp/commit/621d49bc08cc7e3c44a021b1aa101625628778f9) by Jonathan Pyle).
- additional fix for combobox issue ([df677ce](https://github.com/dblevin1/docassemble-webapp/commit/df677ce992aa0c1702d250d6760f375c99964270) by Jonathan Pyle).
- added pagination to get_user_list() and interview_list() and associated API endpoints; removed six support; persistent tasks; secret and current_info; software update order ([3364185](https://github.com/dblevin1/docassemble-webapp/commit/3364185cdf3419eda27edd207cad36d0e11fe5e4) by Jonathan Pyle).
- add another label; manual_line_breaks; DADict true false methods; API sessions in /interviews ([8a914b1](https://github.com/dblevin1/docassemble-webapp/commit/8a914b1b18031c8f03134c9a6476a5ceb400db63) by Jonathan Pyle).
- address autocomplete and show if; PDF checkbox export value; closes #285 ([b57df57](https://github.com/dblevin1/docassemble-webapp/commit/b57df57e243715347266b85bb3c48d35330e7758) by Jonathan Pyle).
- Adds python-in-yaml syntax highlighting to codemirror ([8cf0953](https://github.com/dblevin1/docassemble-webapp/commit/8cf095356eab2a8cf97779159f6fd24911cf3af0) by plocket).
- add_separators; session error redirect url; as_noun change; Dockerfile does upgrade ([54c6816](https://github.com/dblevin1/docassemble-webapp/commit/54c6816acc3f9b7fe25406abcb8a5d270e7113c1) by Jonathan Pyle).
- add python-ldap=3.2.0 resource ([b4c4620](https://github.com/dblevin1/docassemble-webapp/commit/b4c4620ca1145018793f17c3283051f91a5e2367) by Hendrik).
- add_action gathering ([185466a](https://github.com/dblevin1/docassemble-webapp/commit/185466a9daa65f07c19d685abc60220e4c83f8de) by Jonathan Pyle).
- Adding with_for_update ([aa8968c](https://github.com/dblevin1/docassemble-webapp/commit/aa8968c5067dab95b770103aaadcb97de4b7224b) by Jonathan Pyle).
- Additional information in data representation of question ([367c0fc](https://github.com/dblevin1/docassemble-webapp/commit/367c0fc913858842f7ba402a6620bc077556c7a4) by Jonathan Pyle).
- added csrf token to office addin ([72e04e8](https://github.com/dblevin1/docassemble-webapp/commit/72e04e857f4fa483007501068b332480606c0620) by Jonathan Pyle).
- added iterable info to pgvars ([4524af5](https://github.com/dblevin1/docassemble-webapp/commit/4524af53c4208805d616ac586001b6284b8b139e) by Jonathan Pyle).
- additional functions for addin ([d4e745d](https://github.com/dblevin1/docassemble-webapp/commit/d4e745d08288d497feb23d011a43a0e4209fe0f2) by Jonathan Pyle).
- address changes; temp_url bug ([3ed7d5f](https://github.com/dblevin1/docassemble-webapp/commit/3ed7d5f4f9e1729cb3ea190f61cba91a32a5d424) by Jonathan Pyle).
- address autocomplete ([3855f4a](https://github.com/dblevin1/docassemble-webapp/commit/3855f4a33aeb44f2f96d18f595bca24aba5758cd) by Jonathan Pyle).
- Address geolocate and normalize ([bfd064d](https://github.com/dblevin1/docassemble-webapp/commit/bfd064dbe09e503d5ffdebef0d1ba95555e2d36e) by Jonathan Pyle).
- additional fields for json ([7b98d59](https://github.com/dblevin1/docassemble-webapp/commit/7b98d5904431f1e003131c743e12e56b56d01835) by Jonathan Pyle).
- add user page and PDF fields fix ([e35aa48](https://github.com/dblevin1/docassemble-webapp/commit/e35aa482bb38b860d9c1b9012d2f98d6871d61f0) by Jonathan Pyle).
- added traceback in debug mode ([83ed15a](https://github.com/dblevin1/docassemble-webapp/commit/83ed15a33de249927d39139742fcac3eb3be8740) by Jonathan Pyle).
- added Dockerfile ([ec6c3bc](https://github.com/dblevin1/docassemble-webapp/commit/ec6c3bc430c1174e10f9f94fd072e9aabfc48814) by Jonathan Pyle).

### Fixed

- fix trusted hosts str ([23801ad](https://github.com/dblevin1/docassemble-webapp/commit/23801ad9ec3dd55289ee4d96289a98df03f1fa22) by Daniel Blevins).
- fix for sqlalchemy error ([d8e3ea8](https://github.com/dblevin1/docassemble-webapp/commit/d8e3ea80d01f37ef3f16dc87c8fbc5d83079dfed) by Jonathan Pyle).
- fix error with User List ([7c865fc](https://github.com/dblevin1/docassemble-webapp/commit/7c865fc0717c6a5bd8d806cf560fac518e555768) by Jonathan Pyle).
- fixed atomicwrites ([edac40e](https://github.com/dblevin1/docassemble-webapp/commit/edac40e435aba6d38a5b76523de12b65381c92e0) by Jonathan Pyle).
- Fix incorrect function reference ([acf9655](https://github.com/dblevin1/docassemble-webapp/commit/acf96553223e450c2fe685eee1d481decccd8b05) by Quinten Steenhuis).
- fix permissions issue with interview_list ([ecd4cb2](https://github.com/dblevin1/docassemble-webapp/commit/ecd4cb26eac3ad3798348aaeea65f49db1fee453) by Jonathan Pyle).
- fix send_file issue related to new flask version ([74e9c15](https://github.com/dblevin1/docassemble-webapp/commit/74e9c15eccc53187c47addab05d3c922173e138f) by Jonathan Pyle).
- fix error with package update permissions ([268c262](https://github.com/dblevin1/docassemble-webapp/commit/268c2620ea783198648eed3ad634c00bb59e8f40) by Jonathan Pyle).
- fix regarding oauth login redirect ([048abdb](https://github.com/dblevin1/docassemble-webapp/commit/048abdb8457df7a5a3d3fb7b8aa9a07a3e402eff) by Jonathan Pyle).
- Fixes other undeclared variable references in corner cases ([f42e84f](https://github.com/dblevin1/docassemble-webapp/commit/f42e84f92799b6e0e2e64d8379f4fcc01f430d01) by Bryce Willey).
- Fixes `NameError: name 'select' is not defined ([4bd0e0f](https://github.com/dblevin1/docassemble-webapp/commit/4bd0e0fbad0096c0fc21803a9a30cf9d722f5a6f) by Bryce Willey).
- fix regression where a filename from previous versions with multiple spaces would not load ([24fd574](https://github.com/dblevin1/docassemble-webapp/commit/24fd574efae499dc8c2b54c7cd00f22f981286d1) by Eric Tucker).
- Fixes error when you set email on a phone login ([ca26547](https://github.com/dblevin1/docassemble-webapp/commit/ca26547ba878984b4b7782539878ad7789479d8e) by Bryce Willey).
- Fixes `AttributeError` when trying to copy a file ([5199edd](https://github.com/dblevin1/docassemble-webapp/commit/5199edd5ea13da54db230afa67aa0db106cc6d75) by Bryce Willey).
- fix: check there is a domain before using domain to log out ([8f99a8c](https://github.com/dblevin1/docassemble-webapp/commit/8f99a8c5850c276c6ed1804a4748666dec01bee4) by James Cullen).
- fix: correctly log out of keycloak when logout is called ([991ebe6](https://github.com/dblevin1/docassemble-webapp/commit/991ebe6424a40842d4897d926b24ccd97ae2ca0b) by James Cullen).
- fix_up expansion ([9f9372c](https://github.com/dblevin1/docassemble-webapp/commit/9f9372c8f632f225fe613978b687c75fd932b7c5) by Jonathan Pyle).
- fix_up; uses_acroform; qpdf processing on error ([d489700](https://github.com/dblevin1/docassemble-webapp/commit/d4897006bccdee3f01891f504de2635b354059ee) by Jonathan Pyle).
- fix for IE compatibility ([f6af0a7](https://github.com/dblevin1/docassemble-webapp/commit/f6af0a77cda11297e9583595cc49dd149eb9a25c) by Jonathan Pyle).
- fix re group level file permissions ([1c71096](https://github.com/dblevin1/docassemble-webapp/commit/1c7109674441e9023fe9e096d1803f3cd09f2849) by Jonathan Pyle).
- fixed logmessage call that raises a NameError since result is not defined in context ([2f36b6f](https://github.com/dblevin1/docassemble-webapp/commit/2f36b6f7b4bca5bd8c67c15a3974c49d4487d508) by Staffan Malmgren).
- fixed typo ([1c3d1f4](https://github.com/dblevin1/docassemble-webapp/commit/1c3d1f46b4c2001196f3e8421553ebb18dc9ce53) by Jonathan Pyle).
- fix typo in update module ([e88ddfe](https://github.com/dblevin1/docassemble-webapp/commit/e88ddfee0a0261642c54304c71b462273af314ba) by Jonathan Pyle).
- fix logserver configuration ([d67f423](https://github.com/dblevin1/docassemble-webapp/commit/d67f42388be24c9669010388d3ac3ab50120c377) by Jonathan Pyle).
- fix free disk space problem on Python 2.7 ([4307d24](https://github.com/dblevin1/docassemble-webapp/commit/4307d249ea050336ccc6fcefd9bf7109676d917e) by Jonathan Pyle).
- fix for issue with project/package name collision ([ca9ad00](https://github.com/dblevin1/docassemble-webapp/commit/ca9ad002a626c951afbc50b22ebc8a18c6fff5e7) by Jonathan Pyle).
- fix to ajax example ([6a5f77a](https://github.com/dblevin1/docassemble-webapp/commit/6a5f77a70324285dfb1f33192ef211dbcbb4c9a2) by Jonathan Pyle).
- fix for undefine function ([1347150](https://github.com/dblevin1/docassemble-webapp/commit/134715008caff9070813ac1c7ad21b1fe4c89c18) by Jonathan Pyle).
- fix re cloud cache invalidation ([8f1c511](https://github.com/dblevin1/docassemble-webapp/commit/8f1c511832bd5b1e5b46f7d43d1933d4c0a2b90a) by Jonathan Pyle).
- fixed error re Auth0 ([3eb43e0](https://github.com/dblevin1/docassemble-webapp/commit/3eb43e089514bb247dafd2c8cd504a5299abbe1c) by Jonathan Pyle).
- fixes re restarting ([fd35da3](https://github.com/dblevin1/docassemble-webapp/commit/fd35da383ec0f3af7aac77bd5b785ceb199ac5aa) by Jonathan Pyle).
- fixed Python 2 error ([c277361](https://github.com/dblevin1/docassemble-webapp/commit/c277361ad8aa805e4eebef34f812354b17fa0fbe) by Jonathan Pyle).
- fix to issue with actions; field numbers in error; ask_object_type and add_action; new_window sets target ([8b21ddd](https://github.com/dblevin1/docassemble-webapp/commit/8b21ddd5e6b68eeedfcdbe8c8b15ddd97a772cab) by Jonathan Pyle).
- fix to Firefox date entry problem; upgrade Pandoc; more installation in startup process ([47e43b6](https://github.com/dblevin1/docassemble-webapp/commit/47e43b6d984c1a16a77ab537eb418d8febc025a8) by Jonathan Pyle).
- Fix for playground modules issue ([8f7fd34](https://github.com/dblevin1/docassemble-webapp/commit/8f7fd346fdefe140cac2c1fc46fe30552dcbca5d) by Jonathan Pyle).
- fix for unicode issue in markdown documents ([9e14137](https://github.com/dblevin1/docassemble-webapp/commit/9e14137a4ad06e841fa5db8dc19d67b7746c1465) by Jonathan Pyle).
- fix for exporting tables; space_to_underscore change; rows option for text area; spinner on action ([53b99f9](https://github.com/dblevin1/docassemble-webapp/commit/53b99f982b3feca5286d1f2791b3c7b4acf62cf0) by Jonathan Pyle).
- fixes and enhancements for review blocks, tables, navigation bar, reconsider function, slice method ([e794293](https://github.com/dblevin1/docassemble-webapp/commit/e79429370bf8cf664c0d538c5ec71f5fa4c5ffa8) by Jonathan Pyle).
- fix error with create_new_interview ([b7a28bd](https://github.com/dblevin1/docassemble-webapp/commit/b7a28bde66cc900e3ca6f4528816b1a79e98dece) by Jonathan Pyle).
- fix for error with template variables using string indices; start of changes for redaction feature ([b8e4a45](https://github.com/dblevin1/docassemble-webapp/commit/b8e4a453cf35c065825af9e889b68e34eed808ff) by Jonathan Pyle).
- fix re group by error ([0df11f4](https://github.com/dblevin1/docassemble-webapp/commit/0df11f4c0ca7d7600a6de228ea09f0253596f41c) by Jonathan Pyle).
- fixed to error notifications ([1de890c](https://github.com/dblevin1/docassemble-webapp/commit/1de890c9d6f0390e7a3c6869e8263c34aedd96c5) by Jonathan Pyle).
- fix for bootstrap bug on ios mobile ([f1c96ad](https://github.com/dblevin1/docassemble-webapp/commit/f1c96add83b57b9511995aae5f0072ac62c66763) by Jonathan Pyle).
- fix for api where session ID not available in current_info ([7ba70f0](https://github.com/dblevin1/docassemble-webapp/commit/7ba70f05da364d159c572d6ad04294d407ca9d84) by Jonathan Pyle).
- fix uid problem ([77f81d9](https://github.com/dblevin1/docassemble-webapp/commit/77f81d98b65b4e4e18390dca97444ac337b50efb) by Jonathan Pyle).
- fixed docx formatting error ([e56c83a](https://github.com/dblevin1/docassemble-webapp/commit/e56c83ade269f11e5ea331023f980d90cc8a546c) by Jonathan Pyle).
- fix float/int problem with randomforest ([050b807](https://github.com/dblevin1/docassemble-webapp/commit/050b80745045e00a08a2be3b6e44a754bb7e061d) by Jonathan Pyle).
- fix attachment generation problem ([96edbe5](https://github.com/dblevin1/docassemble-webapp/commit/96edbe5e457e529a58046843e0ef95f5db4951c2) by Jonathan Pyle).
- fixes to button javascript, interview encryption ([524350c](https://github.com/dblevin1/docassemble-webapp/commit/524350cc4fd31610c50dc13cb24bb73b8d0b98fd) by Jonathan Pyle).
- fixes of filename handling ([a444ff5](https://github.com/dblevin1/docassemble-webapp/commit/a444ff548c2134ed497d0923990b0f2977878b08) by Jonathan Pyle).
- fix for latest version of flask-user ([9ba1a26](https://github.com/dblevin1/docassemble-webapp/commit/9ba1a26fb03d84a9ffa88c131c4ab612bbc07e0d) by Jonathan Pyle).
- fix CSS typo ([e15b9a9](https://github.com/dblevin1/docassemble-webapp/commit/e15b9a9621596d0c78b0a0c83b7413cbf6847f03) by Jonathan Pyle).
- fix typo ([055a037](https://github.com/dblevin1/docassemble-webapp/commit/055a03752470fbfa93f9895a376983a8dc9c1600) by Jonathan Pyle).
- fix problem with DADict from checkboxes ([1a456ff](https://github.com/dblevin1/docassemble-webapp/commit/1a456ff080584abf55d085ad9adcd9a6a11fda99) by Jonathan Pyle).
- fixes re temp files and images ([db90c74](https://github.com/dblevin1/docassemble-webapp/commit/db90c74eb2829e8e424e6def24be76889e216257) by Jonathan Pyle).
- fix to url finder function ([351198d](https://github.com/dblevin1/docassemble-webapp/commit/351198dd9e1cb7e1c050b89dca615d2e98e5e126) by Jonathan Pyle).
- fix user list error ([8bad432](https://github.com/dblevin1/docassemble-webapp/commit/8bad432b86f44be101befea0c8171c8560d0cd43) by Jonathan Pyle).
- fix edit user profile page error ([440af8d](https://github.com/dblevin1/docassemble-webapp/commit/440af8d61f0fa6260874480ff9f6128b3dbad185) by Jonathan Pyle).
- fix Google login ([55f7ced](https://github.com/dblevin1/docassemble-webapp/commit/55f7ced959a11b75e52f3331f5dbbc6abcd8b3c4) by Jonathan Pyle).
- Fixed update secret problem ([a3da02a](https://github.com/dblevin1/docassemble-webapp/commit/a3da02a5fd2a6214a897458ad03d31ea2662289d) by Jonathan Pyle).
- fix registration form ([0c00932](https://github.com/dblevin1/docassemble-webapp/commit/0c0093253e27c9d9ee5336ed625eccfa5e825787) by Jonathan Pyle).
- fix attorney.yml example ([84a3203](https://github.com/dblevin1/docassemble-webapp/commit/84a320326a50d33063d62d8dc92d7b8eb350c5d4) by Jonathan Pyle).
- fixed unicode issue with loading Markdown files ([92ff035](https://github.com/dblevin1/docassemble-webapp/commit/92ff035b3599db26f7418444b77ccabffd5ba5a8) by Jonathan Pyle).
- fix postgresql bugfix ([53a0436](https://github.com/dblevin1/docassemble-webapp/commit/53a0436e3f89daf10c70a16dd495f81b021b5f8a) by Jonathan Pyle).
- fix missing database columns ([9842932](https://github.com/dblevin1/docassemble-webapp/commit/984293284d0204610cd36039c7436ff47ab66f06) by Jonathan Pyle).
- fix errors ([066a298](https://github.com/dblevin1/docassemble-webapp/commit/066a2983a5805a72fd95767024c69a1f21f64793) by Jonathan Pyle).
- fix playground ([44aa778](https://github.com/dblevin1/docassemble-webapp/commit/44aa778bff4fe2e61c2b9809413feafa18d88b87) by Jonathan Pyle).
- fix screenshots ([fd5d5a3](https://github.com/dblevin1/docassemble-webapp/commit/fd5d5a3a18f74057b62731c622390ec88c606993) by Jonathan Pyle).
- fix chrome problem ([74677b0](https://github.com/dblevin1/docassemble-webapp/commit/74677b02ae4d69a50929272741871f3d40e72c98) by Jonathan Pyle).
- fixed passlib problem ([25d431a](https://github.com/dblevin1/docassemble-webapp/commit/25d431a90650bfddc1c9bdcf0953829bc51d7c8e) by Jonathan Pyle).
- fixed lets encrypt ([2ecb4e5](https://github.com/dblevin1/docassemble-webapp/commit/2ecb4e5aaed418e443f133ad2a125448ca1dda30) by Jonathan Pyle).
- fix playground template file problem ([891028a](https://github.com/dblevin1/docassemble-webapp/commit/891028a2fec7ee02b50bdcb85bb8628a2bcdcc4e) by Jonathan Pyle).
- fixes to install system ([eb2f6d5](https://github.com/dblevin1/docassemble-webapp/commit/eb2f6d5cb59d3aeddab2362574b026a035b5af2b) by Jonathan Pyle).
- fix problem with logging level ([33c944d](https://github.com/dblevin1/docassemble-webapp/commit/33c944d4cfdfae59eb82912b839533046408e167) by Jonathan Pyle).
- fixed up example yaml files ([f736056](https://github.com/dblevin1/docassemble-webapp/commit/f7360560b91cb98ad664885d2bab8db8cfdecdd2) by Jonathan Pyle).
- fix google sign in ([ead7302](https://github.com/dblevin1/docassemble-webapp/commit/ead730291a91938d177a9960f07d9b76c466dd12) by Jonathan Pyle).
- fixed login bugs; auto user creation ([3555f4f](https://github.com/dblevin1/docassemble-webapp/commit/3555f4f71b7b79d39ccd6b02cb5d0c7a79ff7afc) by Jonathan Pyle).
- fixes to signature ([e9d18d7](https://github.com/dblevin1/docassemble-webapp/commit/e9d18d76403587af8bf42611bdfb5a8d1fe7a90d) by Jonathan Pyle).

### Changed

- changes suggested by linter; check in now sends _changed and _initial; prior keyword argument for defined, value, and showifdef; output of countries_list() and states_list() now sorted; states_list() returns empty dictionary on error; support for updating dropdown choices with background_response(); upgraded pikepdf ([50cde95](https://github.com/dblevin1/docassemble-webapp/commit/50cde9528020a50b2790ed478a093ded0d20d6a4) by Jonathan Pyle).
- changed timing of daPageLoad ([4d8377c](https://github.com/dblevin1/docassemble-webapp/commit/4d8377c3f8329a63facc51ba09832e0eae81b6a9) by Jonathan Pyle).
- changelog fix ([51fa7f6](https://github.com/dblevin1/docassemble-webapp/commit/51fa7f64f6f7dfa3cb5d5f88a684ffa25be3d9b2) by Jonathan Pyle).
- changes suggested by linter ([8915265](https://github.com/dblevin1/docassemble-webapp/commit/891526571078e10a44aea0d6716bd66809f4a248) by Jonathan Pyle).
- Change sub update-package headers to h3, not h2 ([2a92c7a](https://github.com/dblevin1/docassemble-webapp/commit/2a92c7a24d9d1ca925326ecc3356fcee331e032c) by Bryce Willey).
- change all_variables so it respects include_internal; add required and aria-required tags; change interview_url so that it accepts only a session; change url_ask so that it can begin with an action and the action does not run twice; fix error in session deletion code ([2580fce](https://github.com/dblevin1/docassemble-webapp/commit/2580fce4590dda013dcfdfc70fa9dec9f8c13982) by Jonathan Pyle).
- changelog ([7050a20](https://github.com/dblevin1/docassemble-webapp/commit/7050a2011240aa8380246328ef5d240c0783ba5b) by Jonathan Pyle).
- changes suggested by linter; API key encryption; admin user context for module loading; Bootstrap typo; machine learning fix ([a23bf74](https://github.com/dblevin1/docassemble-webapp/commit/a23bf7462375eabf450047419fc5808929ef926e) by Jonathan Pyle).
- changelog; better-looking spacing on Playground packages page; fix typo ([8a57b00](https://github.com/dblevin1/docassemble-webapp/commit/8a57b00cd84b1af0f28d159fe6321c3ad1cbd0fa) by Jonathan Pyle).
- changelog; wizard fixes ([ddb806c](https://github.com/dblevin1/docassemble-webapp/commit/ddb806cbd34ffcc7db1876daa8b4fc882752134c) by Jonathan Pyle).
- changelog; startup hook ([4f569dc](https://github.com/dblevin1/docassemble-webapp/commit/4f569dc0e5363b42d70d58d67df5b8e39770c179) by Jonathan Pyle).
- changed example ([de205af](https://github.com/dblevin1/docassemble-webapp/commit/de205afff77d713a49d44af55a97c9466ad4dc84) by Jonathan Pyle).
- changelog; start of table reorder feature ([81b21d0](https://github.com/dblevin1/docassemble-webapp/commit/81b21d07a4f6303e11c849699e595ac10deb3ccb) by Jonathan Pyle).
- Changes for Python 3; fix to foreign key problem ([36d73a4](https://github.com/dblevin1/docassemble-webapp/commit/36d73a4b64e507fc38b9f5be70053bf7491cf61c) by Jonathan Pyle).
- Changes for API interview driving ([a866ad8](https://github.com/dblevin1/docassemble-webapp/commit/a866ad8575508a5202b59d1b5e8d51ab47485ba8) by Jonathan Pyle).
- changelog; cron fix ([62361c8](https://github.com/dblevin1/docassemble-webapp/commit/62361c8796707707458e75ffc482b3a4a02bdebd) by Jonathan Pyle).
- changelog; rollback celery ([0133c50](https://github.com/dblevin1/docassemble-webapp/commit/0133c5065a6c865a5b8123f692e4862d2f25415e) by Jonathan Pyle).
- changelog and example ([612d8ae](https://github.com/dblevin1/docassemble-webapp/commit/612d8ae6ed7b28ba10149fd074de3025883a6406) by Jonathan Pyle).
- changed office addin default URL ([39d4c5d](https://github.com/dblevin1/docassemble-webapp/commit/39d4c5dd38779220e42f4ba3a42c0b1473daeca2) by Jonathan Pyle).
- change to group gathering ([a021331](https://github.com/dblevin1/docassemble-webapp/commit/a021331696b9a65fc28c92b2e5c0bf088319b8ee) by Jonathan Pyle).

### Removed

- removed dependency on py; changes suggested by CodeQL and pylint ([52d2818](https://github.com/dblevin1/docassemble-webapp/commit/52d28184bbeb0fec8dd187d16111434508b9ec7e) by Jonathan Pyle).
- remove sklearn from reserved list ([efa4ccc](https://github.com/dblevin1/docassemble-webapp/commit/efa4cccf3beac19c27eef114bc414562ad540f98) by Jonathan Pyle).
- Remove logs ([bd096bc](https://github.com/dblevin1/docassemble-webapp/commit/bd096bc8c0211621057bae73d14d4a20dff8eac2) by Bryce Willey).
- Removed unnecessary `type` attribute for script ([a4d7a22](https://github.com/dblevin1/docassemble-webapp/commit/a4d7a220f47075b34ca4fd8550d1b5fa3776b790) by Bryce Willey).
- removed unused JavaScript file moment.min.js that raised a dependabot flag ([362753d](https://github.com/dblevin1/docassemble-webapp/commit/362753d8bae5649edd67b8444810625d559bf5df) by Jonathan Pyle).
- Remove unused imports ([577407c](https://github.com/dblevin1/docassemble-webapp/commit/577407c64d5ba5d68023f377190244e7486b5579) by Bryce Willey).
- removed extraneous files; websockets upgrade ([5634ab5](https://github.com/dblevin1/docassemble-webapp/commit/5634ab52de8208de5694ffde80d3833d1543027b) by Jonathan Pyle).
- Removed Python 2.7 compatibility code ([5355944](https://github.com/dblevin1/docassemble-webapp/commit/5355944446441acb95404247a72df996936fae4a) by Jonathan Pyle).
- removed old CORS code ([d62d0a7](https://github.com/dblevin1/docassemble-webapp/commit/d62d0a7b37a09f87db8bdb8174acd29990c92f6e) by Jonathan Pyle).
- removed include_privileges option for get_user_list ([06f3fcd](https://github.com/dblevin1/docassemble-webapp/commit/06f3fcd2abd77ae7a00a11f7c72a713d4f62f205) by Jonathan Pyle).
- Removed log message ([57e79d8](https://github.com/dblevin1/docassemble-webapp/commit/57e79d848b09f72d10ec0665bf2b63f623f1f165) by Jonathan Pyle).
- removed log messages, updated changelog ([8b6ad8f](https://github.com/dblevin1/docassemble-webapp/commit/8b6ad8f69b85e0c59060455762146172ae806564) by Jonathan Pyle).
- removed log messages from upload feature ([8c57cc4](https://github.com/dblevin1/docassemble-webapp/commit/8c57cc4d8ea0964c0b8c8f3f5dd39d89e613791f) by Jonathan Pyle).
- removed static office addin ([d6b22f2](https://github.com/dblevin1/docassemble-webapp/commit/d6b22f209c34a4fa7b87148ad46fcf8a0fd485ae) by Jonathan Pyle).
- removed log messages ([d7530d4](https://github.com/dblevin1/docassemble-webapp/commit/d7530d407e9eb7dbcd550846d2f66cfe95df9fe7) by Jonathan Pyle).
- removed debugging code ([fc34e1e](https://github.com/dblevin1/docassemble-webapp/commit/fc34e1e2be8aa6308b8864b7dcab378f0dbea66d) by Jonathan Pyle).
- removed messages ([06e09bd](https://github.com/dblevin1/docassemble-webapp/commit/06e09bd654a1ee8f5cfb5ecfd4bdd9398db1b32d) by Jonathan Pyle).
- remove log message ([834ac70](https://github.com/dblevin1/docassemble-webapp/commit/834ac70e0229f168f634085da5e6dd2d4a368089) by Jonathan Pyle).
- remove server_name app config ([3cf265f](https://github.com/dblevin1/docassemble-webapp/commit/3cf265ff0d63b6244f5cdebc4b793de9a27aee0a) by Jonathan Pyle).
- removed feature mistakenly added ([fe5156f](https://github.com/dblevin1/docassemble-webapp/commit/fe5156f3e3128ec71f1300b606febc7981c3bf10) by Jonathan Pyle).
- removed timer ([58360b4](https://github.com/dblevin1/docassemble-webapp/commit/58360b419afc934b7971eab25f05b8eb7c250246) by Jonathan Pyle).
- remove current_info dict ([28f7a38](https://github.com/dblevin1/docassemble-webapp/commit/28f7a38a0f254be6d8377b2cc7f6c6c7f07ddfce) by Jonathan Pyle).
- removed GPL software ([b60f49b](https://github.com/dblevin1/docassemble-webapp/commit/b60f49b94ccc8bce7e28f03ebc4dce003122bb9a) by Jonathan Pyle).
- remove distutils ([8366ba8](https://github.com/dblevin1/docassemble-webapp/commit/8366ba8ce33b4be10b490a46b28eb5c152e25b33) by Jonathan Pyle).
- remove pip.utils.logging ([c45391b](https://github.com/dblevin1/docassemble-webapp/commit/c45391bdab06fdef26f15e537ef16215eed69164) by Jonathan Pyle).

## [v1.4.52.2](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.52.2) - 2023-05-26

<small>[Compare with v](https://github.com/dblevin1/docassemble-webapp/compare/v...v1.4.52.2)</small>

### Removed

- remove background_action sleep ([72e6feb](https://github.com/dblevin1/docassemble-webapp/commit/72e6feb065a366063bf6d2d503fd5c5b55d7b8da) by Daniel Blevins).

## [v](https://github.com/dblevin1/docassemble-webapp/releases/tag/v) - 2023-05-19

<small>[Compare with v1.4.51.5](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.5...v)</small>

### Added

- add server init message ([a6bf6bf](https://github.com/dblevin1/docassemble-webapp/commit/a6bf6bfada77a27a24442c74ac4324610956a73d) by Daniel Blevins).

### Fixed

- fix bumpversion config ([36c6e48](https://github.com/dblevin1/docassemble-webapp/commit/36c6e48bb66090aff95ea02dfb79a28c1bc395b8) by Daniel Blevins).

## [v1.4.51.5](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.5) - 2023-05-14

<small>[Compare with v1.4.51.4](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.4...v1.4.51.5)</small>

## [v1.4.51.4](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.4) - 2023-05-13

<small>[Compare with v1.4.51.3](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.3...v1.4.51.4)</small>

## [v1.4.51.3](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.51.3) - 2023-05-13

<small>[Compare with first commit](https://github.com/dblevin1/docassemble-webapp/compare/6a25cb7db0fe630262f242150f23dd518956a3aa...v1.4.51.3)</small>

### Added

- add bumpversion release config ([f905399](https://github.com/dblevin1/docassemble-webapp/commit/f9053991b2fe150a28c34f398cab8a9a54a69b90) by Daniel Blevins).
- add available version badges to updatable packages ([c34935b](https://github.com/dblevin1/docassemble-webapp/commit/c34935bf0dd58d873f43ab772a02229f12bd8da4) by Daniel Blevins).
- add write_pip_conf ([6c9142c](https://github.com/dblevin1/docassemble-webapp/commit/6c9142c156d6fa8c0e919635bde3d03dc0a9548c) by Daniel Blevins).
- add identifier for this package ([3ea6d70](https://github.com/dblevin1/docassemble-webapp/commit/3ea6d7017f9f298b586c8a517b868e812b3e098b) by Daniel Blevins).
- add gitignore ([dfabe2d](https://github.com/dblevin1/docassemble-webapp/commit/dfabe2dc846cae0230d5c4b2413932fbd7210ccc) by Daniel Blevins).
- added all and any as jinja2 filters; fixed issue with validation messages of custom datatypes when used with show if ([35e6c25](https://github.com/dblevin1/docassemble-webapp/commit/35e6c254ae7bc827bffa807c0697cc48fc641e74) by Jonathan Pyle).
- additional pikepdf fixes ([4c540aa](https://github.com/dblevin1/docassemble-webapp/commit/4c540aa881d9ebaa7ea0cf1f3a1508ceed53e3d0) by Jonathan Pyle).
- Add error trace and log to context of custom error handlers ([3b87316](https://github.com/dblevin1/docassemble-webapp/commit/3b87316c5e6e53a62bca327b6fd7a023c51a17de) by Quinten Steenhuis).
- address autocomplete options; hidden input type; Configuration searching ([3ee3640](https://github.com/dblevin1/docassemble-webapp/commit/3ee364068b1a66426a72454e54267f40201f1dab) by Jonathan Pyle).
- added 'ip address ban enabled' Configuration directive; fixed translation on logout page; faster query for sessions to delete when deleting sessions using interview_list and a query or tag filtering; fix session_id parameter for resume_url; changed logrotate configuration to avoid error messages ([b028fdc](https://github.com/dblevin1/docassemble-webapp/commit/b028fdc069fc98f1611054dab474075c6164637e) by Jonathan Pyle).
- added the Configuration directive allow configuration editing and the Docker environment variable DAALLOWCONFIGURATIONEDITING to control whether the administrator can edit the Configuration; added Docker environment variables DADEBUG and DAENABLEPLAYGROUND; the allow updates and enable playground directives now affect access to API endpoints ([539a95b](https://github.com/dblevin1/docassemble-webapp/commit/539a95b6d351088d0792914775139c4b8433130f) by Jonathan Pyle).
- Added pip index url and pip extra index urls; added insertion_order option for .true_values(); allow API keys to be passed as bearer tokens; removed pathlib as a dependency; yesnoradio now sets variable to None if not required and not answered; fix issues with target_number's data type; update the exports of docassemble.base.legal so that they include everything exported by docassemble.base.util; issue with review blocks where set and follow up were not recognized if using the older syntax; issue with send_email() and send_sms() not processing DAList recipients; issue with navigation sections showing already-visited sections as not visited; fixed four-second timeout problem with error action. ([7c26c58](https://github.com/dblevin1/docassemble-webapp/commit/7c26c585f95633137c1ff880d2690afac9be9cec) by Jonathan Pyle).
- Add an explicit Schema.org item to the webpage ([d315142](https://github.com/dblevin1/docassemble-webapp/commit/d315142acecf01cf18d14f872ce66a83a3b51f46) by Bryce Willey).
- Add a aria-label to the progress bar ([2103763](https://github.com/dblevin1/docassemble-webapp/commit/2103763cc264caadc86a4c5f15e549c3dd310761) by Bryce Willey).
- Added optgroups to manual select fields, and to without 'fields' too ([dca27e3](https://github.com/dblevin1/docassemble-webapp/commit/dca27e3a68abf0223db1f6769ec71b927cd898fc) by Bryce Willey).
- Add provision for github PAT to install on server ([1f04f6a](https://github.com/dblevin1/docassemble-webapp/commit/1f04f6ab86148956c3594d9bac0579fb06d7a752) by plocket).
- address autocomplete trigger of change event; run preliminary assemble for checkin action ([355806c](https://github.com/dblevin1/docassemble-webapp/commit/355806c0240e99a36f735cbfcff182bfc13b089a) by Jonathan Pyle).
- added descriptive log messages to initialize.sh; added traceback to failure to assemble API error; changed the way the restart screen deals with ajax timeouts; avoided possibly duplicative install table add row command; fixed issue with None not appearing by default in tri-state input elements; fixed issue with code-generated checkbox fields where input was not accepted ([cda70a9](https://github.com/dblevin1/docassemble-webapp/commit/cda70a9ccedb10347a8d29be1326e67f2241e081) by Jonathan Pyle).
- additional on_failure and on_success options for DAWeb methods; random instance name for pdf_concatenate results; longer poll delay in package management UI ([486d37b](https://github.com/dblevin1/docassemble-webapp/commit/486d37b888ebc58c03e1684afa9801343614aea7) by Jonathan Pyle).
- added Jinja2 preprocessor feature; adjusted for ARM compatibility by disabling DAGoogleAPI's dependency; adjusted for xspace bug in new version of Pandoc; better removal of servers from supervisors list if they are non-responsive ([c3ecd3f](https://github.com/dblevin1/docassemble-webapp/commit/c3ecd3f37cbc27ed133c58f4420f245032ec2d0f) by Jonathan Pyle).
- additional input sanitizing for admin and developers ([621d49b](https://github.com/dblevin1/docassemble-webapp/commit/621d49bc08cc7e3c44a021b1aa101625628778f9) by Jonathan Pyle).
- additional fix for combobox issue ([df677ce](https://github.com/dblevin1/docassemble-webapp/commit/df677ce992aa0c1702d250d6760f375c99964270) by Jonathan Pyle).
- added pagination to get_user_list() and interview_list() and associated API endpoints; removed six support; persistent tasks; secret and current_info; software update order ([3364185](https://github.com/dblevin1/docassemble-webapp/commit/3364185cdf3419eda27edd207cad36d0e11fe5e4) by Jonathan Pyle).
- add another label; manual_line_breaks; DADict true false methods; API sessions in /interviews ([8a914b1](https://github.com/dblevin1/docassemble-webapp/commit/8a914b1b18031c8f03134c9a6476a5ceb400db63) by Jonathan Pyle).
- address autocomplete and show if; PDF checkbox export value; closes #285 ([b57df57](https://github.com/dblevin1/docassemble-webapp/commit/b57df57e243715347266b85bb3c48d35330e7758) by Jonathan Pyle).
- Adds python-in-yaml syntax highlighting to codemirror ([8cf0953](https://github.com/dblevin1/docassemble-webapp/commit/8cf095356eab2a8cf97779159f6fd24911cf3af0) by plocket).
- add_separators; session error redirect url; as_noun change; Dockerfile does upgrade ([54c6816](https://github.com/dblevin1/docassemble-webapp/commit/54c6816acc3f9b7fe25406abcb8a5d270e7113c1) by Jonathan Pyle).
- add python-ldap=3.2.0 resource ([b4c4620](https://github.com/dblevin1/docassemble-webapp/commit/b4c4620ca1145018793f17c3283051f91a5e2367) by Hendrik).
- add_action gathering ([185466a](https://github.com/dblevin1/docassemble-webapp/commit/185466a9daa65f07c19d685abc60220e4c83f8de) by Jonathan Pyle).
- Adding with_for_update ([aa8968c](https://github.com/dblevin1/docassemble-webapp/commit/aa8968c5067dab95b770103aaadcb97de4b7224b) by Jonathan Pyle).
- Additional information in data representation of question ([367c0fc](https://github.com/dblevin1/docassemble-webapp/commit/367c0fc913858842f7ba402a6620bc077556c7a4) by Jonathan Pyle).
- added csrf token to office addin ([72e04e8](https://github.com/dblevin1/docassemble-webapp/commit/72e04e857f4fa483007501068b332480606c0620) by Jonathan Pyle).
- added iterable info to pgvars ([4524af5](https://github.com/dblevin1/docassemble-webapp/commit/4524af53c4208805d616ac586001b6284b8b139e) by Jonathan Pyle).
- additional functions for addin ([d4e745d](https://github.com/dblevin1/docassemble-webapp/commit/d4e745d08288d497feb23d011a43a0e4209fe0f2) by Jonathan Pyle).
- address changes; temp_url bug ([3ed7d5f](https://github.com/dblevin1/docassemble-webapp/commit/3ed7d5f4f9e1729cb3ea190f61cba91a32a5d424) by Jonathan Pyle).
- address autocomplete ([3855f4a](https://github.com/dblevin1/docassemble-webapp/commit/3855f4a33aeb44f2f96d18f595bca24aba5758cd) by Jonathan Pyle).
- Address geolocate and normalize ([bfd064d](https://github.com/dblevin1/docassemble-webapp/commit/bfd064dbe09e503d5ffdebef0d1ba95555e2d36e) by Jonathan Pyle).
- additional fields for json ([7b98d59](https://github.com/dblevin1/docassemble-webapp/commit/7b98d5904431f1e003131c743e12e56b56d01835) by Jonathan Pyle).
- add user page and PDF fields fix ([e35aa48](https://github.com/dblevin1/docassemble-webapp/commit/e35aa482bb38b860d9c1b9012d2f98d6871d61f0) by Jonathan Pyle).
- added traceback in debug mode ([83ed15a](https://github.com/dblevin1/docassemble-webapp/commit/83ed15a33de249927d39139742fcac3eb3be8740) by Jonathan Pyle).
- added Dockerfile ([ec6c3bc](https://github.com/dblevin1/docassemble-webapp/commit/ec6c3bc430c1174e10f9f94fd072e9aabfc48814) by Jonathan Pyle).

### Fixed

- fix trusted hosts str ([23801ad](https://github.com/dblevin1/docassemble-webapp/commit/23801ad9ec3dd55289ee4d96289a98df03f1fa22) by Daniel Blevins).
- fix for sqlalchemy error ([d8e3ea8](https://github.com/dblevin1/docassemble-webapp/commit/d8e3ea80d01f37ef3f16dc87c8fbc5d83079dfed) by Jonathan Pyle).
- fix error with User List ([7c865fc](https://github.com/dblevin1/docassemble-webapp/commit/7c865fc0717c6a5bd8d806cf560fac518e555768) by Jonathan Pyle).
- fixed atomicwrites ([edac40e](https://github.com/dblevin1/docassemble-webapp/commit/edac40e435aba6d38a5b76523de12b65381c92e0) by Jonathan Pyle).
- Fix incorrect function reference ([acf9655](https://github.com/dblevin1/docassemble-webapp/commit/acf96553223e450c2fe685eee1d481decccd8b05) by Quinten Steenhuis).
- fix permissions issue with interview_list ([ecd4cb2](https://github.com/dblevin1/docassemble-webapp/commit/ecd4cb26eac3ad3798348aaeea65f49db1fee453) by Jonathan Pyle).
- fix send_file issue related to new flask version ([74e9c15](https://github.com/dblevin1/docassemble-webapp/commit/74e9c15eccc53187c47addab05d3c922173e138f) by Jonathan Pyle).
- fix error with package update permissions ([268c262](https://github.com/dblevin1/docassemble-webapp/commit/268c2620ea783198648eed3ad634c00bb59e8f40) by Jonathan Pyle).
- fix regarding oauth login redirect ([048abdb](https://github.com/dblevin1/docassemble-webapp/commit/048abdb8457df7a5a3d3fb7b8aa9a07a3e402eff) by Jonathan Pyle).
- Fixes other undeclared variable references in corner cases ([f42e84f](https://github.com/dblevin1/docassemble-webapp/commit/f42e84f92799b6e0e2e64d8379f4fcc01f430d01) by Bryce Willey).
- Fixes `NameError: name 'select' is not defined ([4bd0e0f](https://github.com/dblevin1/docassemble-webapp/commit/4bd0e0fbad0096c0fc21803a9a30cf9d722f5a6f) by Bryce Willey).
- fix regression where a filename from previous versions with multiple spaces would not load ([24fd574](https://github.com/dblevin1/docassemble-webapp/commit/24fd574efae499dc8c2b54c7cd00f22f981286d1) by Eric Tucker).
- Fixes error when you set email on a phone login ([ca26547](https://github.com/dblevin1/docassemble-webapp/commit/ca26547ba878984b4b7782539878ad7789479d8e) by Bryce Willey).
- Fixes `AttributeError` when trying to copy a file ([5199edd](https://github.com/dblevin1/docassemble-webapp/commit/5199edd5ea13da54db230afa67aa0db106cc6d75) by Bryce Willey).
- fix: check there is a domain before using domain to log out ([8f99a8c](https://github.com/dblevin1/docassemble-webapp/commit/8f99a8c5850c276c6ed1804a4748666dec01bee4) by James Cullen).
- fix: correctly log out of keycloak when logout is called ([991ebe6](https://github.com/dblevin1/docassemble-webapp/commit/991ebe6424a40842d4897d926b24ccd97ae2ca0b) by James Cullen).
- fix_up expansion ([9f9372c](https://github.com/dblevin1/docassemble-webapp/commit/9f9372c8f632f225fe613978b687c75fd932b7c5) by Jonathan Pyle).
- fix_up; uses_acroform; qpdf processing on error ([d489700](https://github.com/dblevin1/docassemble-webapp/commit/d4897006bccdee3f01891f504de2635b354059ee) by Jonathan Pyle).
- fix for IE compatibility ([f6af0a7](https://github.com/dblevin1/docassemble-webapp/commit/f6af0a77cda11297e9583595cc49dd149eb9a25c) by Jonathan Pyle).
- fix re group level file permissions ([1c71096](https://github.com/dblevin1/docassemble-webapp/commit/1c7109674441e9023fe9e096d1803f3cd09f2849) by Jonathan Pyle).
- fixed logmessage call that raises a NameError since result is not defined in context ([2f36b6f](https://github.com/dblevin1/docassemble-webapp/commit/2f36b6f7b4bca5bd8c67c15a3974c49d4487d508) by Staffan Malmgren).
- fixed typo ([1c3d1f4](https://github.com/dblevin1/docassemble-webapp/commit/1c3d1f46b4c2001196f3e8421553ebb18dc9ce53) by Jonathan Pyle).
- fix typo in update module ([e88ddfe](https://github.com/dblevin1/docassemble-webapp/commit/e88ddfee0a0261642c54304c71b462273af314ba) by Jonathan Pyle).
- fix logserver configuration ([d67f423](https://github.com/dblevin1/docassemble-webapp/commit/d67f42388be24c9669010388d3ac3ab50120c377) by Jonathan Pyle).
- fix free disk space problem on Python 2.7 ([4307d24](https://github.com/dblevin1/docassemble-webapp/commit/4307d249ea050336ccc6fcefd9bf7109676d917e) by Jonathan Pyle).
- fix for issue with project/package name collision ([ca9ad00](https://github.com/dblevin1/docassemble-webapp/commit/ca9ad002a626c951afbc50b22ebc8a18c6fff5e7) by Jonathan Pyle).
- fix to ajax example ([6a5f77a](https://github.com/dblevin1/docassemble-webapp/commit/6a5f77a70324285dfb1f33192ef211dbcbb4c9a2) by Jonathan Pyle).
- fix for undefine function ([1347150](https://github.com/dblevin1/docassemble-webapp/commit/134715008caff9070813ac1c7ad21b1fe4c89c18) by Jonathan Pyle).
- fix re cloud cache invalidation ([8f1c511](https://github.com/dblevin1/docassemble-webapp/commit/8f1c511832bd5b1e5b46f7d43d1933d4c0a2b90a) by Jonathan Pyle).
- fixed error re Auth0 ([3eb43e0](https://github.com/dblevin1/docassemble-webapp/commit/3eb43e089514bb247dafd2c8cd504a5299abbe1c) by Jonathan Pyle).
- fixes re restarting ([fd35da3](https://github.com/dblevin1/docassemble-webapp/commit/fd35da383ec0f3af7aac77bd5b785ceb199ac5aa) by Jonathan Pyle).
- fixed Python 2 error ([c277361](https://github.com/dblevin1/docassemble-webapp/commit/c277361ad8aa805e4eebef34f812354b17fa0fbe) by Jonathan Pyle).
- fix to issue with actions; field numbers in error; ask_object_type and add_action; new_window sets target ([8b21ddd](https://github.com/dblevin1/docassemble-webapp/commit/8b21ddd5e6b68eeedfcdbe8c8b15ddd97a772cab) by Jonathan Pyle).
- fix to Firefox date entry problem; upgrade Pandoc; more installation in startup process ([47e43b6](https://github.com/dblevin1/docassemble-webapp/commit/47e43b6d984c1a16a77ab537eb418d8febc025a8) by Jonathan Pyle).
- Fix for playground modules issue ([8f7fd34](https://github.com/dblevin1/docassemble-webapp/commit/8f7fd346fdefe140cac2c1fc46fe30552dcbca5d) by Jonathan Pyle).
- fix for unicode issue in markdown documents ([9e14137](https://github.com/dblevin1/docassemble-webapp/commit/9e14137a4ad06e841fa5db8dc19d67b7746c1465) by Jonathan Pyle).
- fix for exporting tables; space_to_underscore change; rows option for text area; spinner on action ([53b99f9](https://github.com/dblevin1/docassemble-webapp/commit/53b99f982b3feca5286d1f2791b3c7b4acf62cf0) by Jonathan Pyle).
- fixes and enhancements for review blocks, tables, navigation bar, reconsider function, slice method ([e794293](https://github.com/dblevin1/docassemble-webapp/commit/e79429370bf8cf664c0d538c5ec71f5fa4c5ffa8) by Jonathan Pyle).
- fix error with create_new_interview ([b7a28bd](https://github.com/dblevin1/docassemble-webapp/commit/b7a28bde66cc900e3ca6f4528816b1a79e98dece) by Jonathan Pyle).
- fix for error with template variables using string indices; start of changes for redaction feature ([b8e4a45](https://github.com/dblevin1/docassemble-webapp/commit/b8e4a453cf35c065825af9e889b68e34eed808ff) by Jonathan Pyle).
- fix re group by error ([0df11f4](https://github.com/dblevin1/docassemble-webapp/commit/0df11f4c0ca7d7600a6de228ea09f0253596f41c) by Jonathan Pyle).
- fixed to error notifications ([1de890c](https://github.com/dblevin1/docassemble-webapp/commit/1de890c9d6f0390e7a3c6869e8263c34aedd96c5) by Jonathan Pyle).
- fix for bootstrap bug on ios mobile ([f1c96ad](https://github.com/dblevin1/docassemble-webapp/commit/f1c96add83b57b9511995aae5f0072ac62c66763) by Jonathan Pyle).
- fix for api where session ID not available in current_info ([7ba70f0](https://github.com/dblevin1/docassemble-webapp/commit/7ba70f05da364d159c572d6ad04294d407ca9d84) by Jonathan Pyle).
- fix uid problem ([77f81d9](https://github.com/dblevin1/docassemble-webapp/commit/77f81d98b65b4e4e18390dca97444ac337b50efb) by Jonathan Pyle).
- fixed docx formatting error ([e56c83a](https://github.com/dblevin1/docassemble-webapp/commit/e56c83ade269f11e5ea331023f980d90cc8a546c) by Jonathan Pyle).
- fix float/int problem with randomforest ([050b807](https://github.com/dblevin1/docassemble-webapp/commit/050b80745045e00a08a2be3b6e44a754bb7e061d) by Jonathan Pyle).
- fix attachment generation problem ([96edbe5](https://github.com/dblevin1/docassemble-webapp/commit/96edbe5e457e529a58046843e0ef95f5db4951c2) by Jonathan Pyle).
- fixes to button javascript, interview encryption ([524350c](https://github.com/dblevin1/docassemble-webapp/commit/524350cc4fd31610c50dc13cb24bb73b8d0b98fd) by Jonathan Pyle).
- fixes of filename handling ([a444ff5](https://github.com/dblevin1/docassemble-webapp/commit/a444ff548c2134ed497d0923990b0f2977878b08) by Jonathan Pyle).
- fix for latest version of flask-user ([9ba1a26](https://github.com/dblevin1/docassemble-webapp/commit/9ba1a26fb03d84a9ffa88c131c4ab612bbc07e0d) by Jonathan Pyle).
- fix CSS typo ([e15b9a9](https://github.com/dblevin1/docassemble-webapp/commit/e15b9a9621596d0c78b0a0c83b7413cbf6847f03) by Jonathan Pyle).
- fix typo ([055a037](https://github.com/dblevin1/docassemble-webapp/commit/055a03752470fbfa93f9895a376983a8dc9c1600) by Jonathan Pyle).
- fix problem with DADict from checkboxes ([1a456ff](https://github.com/dblevin1/docassemble-webapp/commit/1a456ff080584abf55d085ad9adcd9a6a11fda99) by Jonathan Pyle).
- fixes re temp files and images ([db90c74](https://github.com/dblevin1/docassemble-webapp/commit/db90c74eb2829e8e424e6def24be76889e216257) by Jonathan Pyle).
- fix to url finder function ([351198d](https://github.com/dblevin1/docassemble-webapp/commit/351198dd9e1cb7e1c050b89dca615d2e98e5e126) by Jonathan Pyle).
- fix user list error ([8bad432](https://github.com/dblevin1/docassemble-webapp/commit/8bad432b86f44be101befea0c8171c8560d0cd43) by Jonathan Pyle).
- fix edit user profile page error ([440af8d](https://github.com/dblevin1/docassemble-webapp/commit/440af8d61f0fa6260874480ff9f6128b3dbad185) by Jonathan Pyle).
- fix Google login ([55f7ced](https://github.com/dblevin1/docassemble-webapp/commit/55f7ced959a11b75e52f3331f5dbbc6abcd8b3c4) by Jonathan Pyle).
- Fixed update secret problem ([a3da02a](https://github.com/dblevin1/docassemble-webapp/commit/a3da02a5fd2a6214a897458ad03d31ea2662289d) by Jonathan Pyle).
- fix registration form ([0c00932](https://github.com/dblevin1/docassemble-webapp/commit/0c0093253e27c9d9ee5336ed625eccfa5e825787) by Jonathan Pyle).
- fix attorney.yml example ([84a3203](https://github.com/dblevin1/docassemble-webapp/commit/84a320326a50d33063d62d8dc92d7b8eb350c5d4) by Jonathan Pyle).
- fixed unicode issue with loading Markdown files ([92ff035](https://github.com/dblevin1/docassemble-webapp/commit/92ff035b3599db26f7418444b77ccabffd5ba5a8) by Jonathan Pyle).
- fix postgresql bugfix ([53a0436](https://github.com/dblevin1/docassemble-webapp/commit/53a0436e3f89daf10c70a16dd495f81b021b5f8a) by Jonathan Pyle).
- fix missing database columns ([9842932](https://github.com/dblevin1/docassemble-webapp/commit/984293284d0204610cd36039c7436ff47ab66f06) by Jonathan Pyle).
- fix errors ([066a298](https://github.com/dblevin1/docassemble-webapp/commit/066a2983a5805a72fd95767024c69a1f21f64793) by Jonathan Pyle).
- fix playground ([44aa778](https://github.com/dblevin1/docassemble-webapp/commit/44aa778bff4fe2e61c2b9809413feafa18d88b87) by Jonathan Pyle).
- fix screenshots ([fd5d5a3](https://github.com/dblevin1/docassemble-webapp/commit/fd5d5a3a18f74057b62731c622390ec88c606993) by Jonathan Pyle).
- fix chrome problem ([74677b0](https://github.com/dblevin1/docassemble-webapp/commit/74677b02ae4d69a50929272741871f3d40e72c98) by Jonathan Pyle).
- fixed passlib problem ([25d431a](https://github.com/dblevin1/docassemble-webapp/commit/25d431a90650bfddc1c9bdcf0953829bc51d7c8e) by Jonathan Pyle).
- fixed lets encrypt ([2ecb4e5](https://github.com/dblevin1/docassemble-webapp/commit/2ecb4e5aaed418e443f133ad2a125448ca1dda30) by Jonathan Pyle).
- fix playground template file problem ([891028a](https://github.com/dblevin1/docassemble-webapp/commit/891028a2fec7ee02b50bdcb85bb8628a2bcdcc4e) by Jonathan Pyle).
- fixes to install system ([eb2f6d5](https://github.com/dblevin1/docassemble-webapp/commit/eb2f6d5cb59d3aeddab2362574b026a035b5af2b) by Jonathan Pyle).
- fix problem with logging level ([33c944d](https://github.com/dblevin1/docassemble-webapp/commit/33c944d4cfdfae59eb82912b839533046408e167) by Jonathan Pyle).
- fixed up example yaml files ([f736056](https://github.com/dblevin1/docassemble-webapp/commit/f7360560b91cb98ad664885d2bab8db8cfdecdd2) by Jonathan Pyle).
- fix google sign in ([ead7302](https://github.com/dblevin1/docassemble-webapp/commit/ead730291a91938d177a9960f07d9b76c466dd12) by Jonathan Pyle).
- fixed login bugs; auto user creation ([3555f4f](https://github.com/dblevin1/docassemble-webapp/commit/3555f4f71b7b79d39ccd6b02cb5d0c7a79ff7afc) by Jonathan Pyle).
- fixes to signature ([e9d18d7](https://github.com/dblevin1/docassemble-webapp/commit/e9d18d76403587af8bf42611bdfb5a8d1fe7a90d) by Jonathan Pyle).

### Changed

- changes suggested by linter; check in now sends _changed and _initial; prior keyword argument for defined, value, and showifdef; output of countries_list() and states_list() now sorted; states_list() returns empty dictionary on error; support for updating dropdown choices with background_response(); upgraded pikepdf ([50cde95](https://github.com/dblevin1/docassemble-webapp/commit/50cde9528020a50b2790ed478a093ded0d20d6a4) by Jonathan Pyle).
- changed timing of daPageLoad ([4d8377c](https://github.com/dblevin1/docassemble-webapp/commit/4d8377c3f8329a63facc51ba09832e0eae81b6a9) by Jonathan Pyle).
- changelog fix ([51fa7f6](https://github.com/dblevin1/docassemble-webapp/commit/51fa7f64f6f7dfa3cb5d5f88a684ffa25be3d9b2) by Jonathan Pyle).
- changes suggested by linter ([8915265](https://github.com/dblevin1/docassemble-webapp/commit/891526571078e10a44aea0d6716bd66809f4a248) by Jonathan Pyle).
- Change sub update-package headers to h3, not h2 ([2a92c7a](https://github.com/dblevin1/docassemble-webapp/commit/2a92c7a24d9d1ca925326ecc3356fcee331e032c) by Bryce Willey).
- change all_variables so it respects include_internal; add required and aria-required tags; change interview_url so that it accepts only a session; change url_ask so that it can begin with an action and the action does not run twice; fix error in session deletion code ([2580fce](https://github.com/dblevin1/docassemble-webapp/commit/2580fce4590dda013dcfdfc70fa9dec9f8c13982) by Jonathan Pyle).
- changelog ([7050a20](https://github.com/dblevin1/docassemble-webapp/commit/7050a2011240aa8380246328ef5d240c0783ba5b) by Jonathan Pyle).
- changes suggested by linter; API key encryption; admin user context for module loading; Bootstrap typo; machine learning fix ([a23bf74](https://github.com/dblevin1/docassemble-webapp/commit/a23bf7462375eabf450047419fc5808929ef926e) by Jonathan Pyle).
- changelog; better-looking spacing on Playground packages page; fix typo ([8a57b00](https://github.com/dblevin1/docassemble-webapp/commit/8a57b00cd84b1af0f28d159fe6321c3ad1cbd0fa) by Jonathan Pyle).
- changelog; wizard fixes ([ddb806c](https://github.com/dblevin1/docassemble-webapp/commit/ddb806cbd34ffcc7db1876daa8b4fc882752134c) by Jonathan Pyle).
- changelog; startup hook ([4f569dc](https://github.com/dblevin1/docassemble-webapp/commit/4f569dc0e5363b42d70d58d67df5b8e39770c179) by Jonathan Pyle).
- changed example ([de205af](https://github.com/dblevin1/docassemble-webapp/commit/de205afff77d713a49d44af55a97c9466ad4dc84) by Jonathan Pyle).
- changelog; start of table reorder feature ([81b21d0](https://github.com/dblevin1/docassemble-webapp/commit/81b21d07a4f6303e11c849699e595ac10deb3ccb) by Jonathan Pyle).
- Changes for Python 3; fix to foreign key problem ([36d73a4](https://github.com/dblevin1/docassemble-webapp/commit/36d73a4b64e507fc38b9f5be70053bf7491cf61c) by Jonathan Pyle).
- Changes for API interview driving ([a866ad8](https://github.com/dblevin1/docassemble-webapp/commit/a866ad8575508a5202b59d1b5e8d51ab47485ba8) by Jonathan Pyle).
- changelog; cron fix ([62361c8](https://github.com/dblevin1/docassemble-webapp/commit/62361c8796707707458e75ffc482b3a4a02bdebd) by Jonathan Pyle).
- changelog; rollback celery ([0133c50](https://github.com/dblevin1/docassemble-webapp/commit/0133c5065a6c865a5b8123f692e4862d2f25415e) by Jonathan Pyle).
- changelog and example ([612d8ae](https://github.com/dblevin1/docassemble-webapp/commit/612d8ae6ed7b28ba10149fd074de3025883a6406) by Jonathan Pyle).
- changed office addin default URL ([39d4c5d](https://github.com/dblevin1/docassemble-webapp/commit/39d4c5dd38779220e42f4ba3a42c0b1473daeca2) by Jonathan Pyle).
- change to group gathering ([a021331](https://github.com/dblevin1/docassemble-webapp/commit/a021331696b9a65fc28c92b2e5c0bf088319b8ee) by Jonathan Pyle).

### Removed

- removed dependency on py; changes suggested by CodeQL and pylint ([52d2818](https://github.com/dblevin1/docassemble-webapp/commit/52d28184bbeb0fec8dd187d16111434508b9ec7e) by Jonathan Pyle).
- remove sklearn from reserved list ([efa4ccc](https://github.com/dblevin1/docassemble-webapp/commit/efa4cccf3beac19c27eef114bc414562ad540f98) by Jonathan Pyle).
- Remove logs ([bd096bc](https://github.com/dblevin1/docassemble-webapp/commit/bd096bc8c0211621057bae73d14d4a20dff8eac2) by Bryce Willey).
- Removed unnecessary `type` attribute for script ([a4d7a22](https://github.com/dblevin1/docassemble-webapp/commit/a4d7a220f47075b34ca4fd8550d1b5fa3776b790) by Bryce Willey).
- removed unused JavaScript file moment.min.js that raised a dependabot flag ([362753d](https://github.com/dblevin1/docassemble-webapp/commit/362753d8bae5649edd67b8444810625d559bf5df) by Jonathan Pyle).
- Remove unused imports ([577407c](https://github.com/dblevin1/docassemble-webapp/commit/577407c64d5ba5d68023f377190244e7486b5579) by Bryce Willey).
- removed extraneous files; websockets upgrade ([5634ab5](https://github.com/dblevin1/docassemble-webapp/commit/5634ab52de8208de5694ffde80d3833d1543027b) by Jonathan Pyle).
- Removed Python 2.7 compatibility code ([5355944](https://github.com/dblevin1/docassemble-webapp/commit/5355944446441acb95404247a72df996936fae4a) by Jonathan Pyle).
- removed old CORS code ([d62d0a7](https://github.com/dblevin1/docassemble-webapp/commit/d62d0a7b37a09f87db8bdb8174acd29990c92f6e) by Jonathan Pyle).
- removed include_privileges option for get_user_list ([06f3fcd](https://github.com/dblevin1/docassemble-webapp/commit/06f3fcd2abd77ae7a00a11f7c72a713d4f62f205) by Jonathan Pyle).
- Removed log message ([57e79d8](https://github.com/dblevin1/docassemble-webapp/commit/57e79d848b09f72d10ec0665bf2b63f623f1f165) by Jonathan Pyle).
- removed log messages, updated changelog ([8b6ad8f](https://github.com/dblevin1/docassemble-webapp/commit/8b6ad8f69b85e0c59060455762146172ae806564) by Jonathan Pyle).
- removed log messages from upload feature ([8c57cc4](https://github.com/dblevin1/docassemble-webapp/commit/8c57cc4d8ea0964c0b8c8f3f5dd39d89e613791f) by Jonathan Pyle).
- removed static office addin ([d6b22f2](https://github.com/dblevin1/docassemble-webapp/commit/d6b22f209c34a4fa7b87148ad46fcf8a0fd485ae) by Jonathan Pyle).
- removed log messages ([d7530d4](https://github.com/dblevin1/docassemble-webapp/commit/d7530d407e9eb7dbcd550846d2f66cfe95df9fe7) by Jonathan Pyle).
- removed debugging code ([fc34e1e](https://github.com/dblevin1/docassemble-webapp/commit/fc34e1e2be8aa6308b8864b7dcab378f0dbea66d) by Jonathan Pyle).
- removed messages ([06e09bd](https://github.com/dblevin1/docassemble-webapp/commit/06e09bd654a1ee8f5cfb5ecfd4bdd9398db1b32d) by Jonathan Pyle).
- remove log message ([834ac70](https://github.com/dblevin1/docassemble-webapp/commit/834ac70e0229f168f634085da5e6dd2d4a368089) by Jonathan Pyle).
- remove server_name app config ([3cf265f](https://github.com/dblevin1/docassemble-webapp/commit/3cf265ff0d63b6244f5cdebc4b793de9a27aee0a) by Jonathan Pyle).
- removed feature mistakenly added ([fe5156f](https://github.com/dblevin1/docassemble-webapp/commit/fe5156f3e3128ec71f1300b606febc7981c3bf10) by Jonathan Pyle).
- removed timer ([58360b4](https://github.com/dblevin1/docassemble-webapp/commit/58360b419afc934b7971eab25f05b8eb7c250246) by Jonathan Pyle).
- remove current_info dict ([28f7a38](https://github.com/dblevin1/docassemble-webapp/commit/28f7a38a0f254be6d8377b2cc7f6c6c7f07ddfce) by Jonathan Pyle).
- removed GPL software ([b60f49b](https://github.com/dblevin1/docassemble-webapp/commit/b60f49b94ccc8bce7e28f03ebc4dce003122bb9a) by Jonathan Pyle).
- remove distutils ([8366ba8](https://github.com/dblevin1/docassemble-webapp/commit/8366ba8ce33b4be10b490a46b28eb5c152e25b33) by Jonathan Pyle).
- remove pip.utils.logging ([c45391b](https://github.com/dblevin1/docassemble-webapp/commit/c45391bdab06fdef26f15e537ef16215eed69164) by Jonathan Pyle).

## [v1.4.52.1](https://github.com/dblevin1/docassemble-webapp/releases/tag/v1.4.52.1) - 2023-05-19

<small>[Compare with v1.4.51.5](https://github.com/dblevin1/docassemble-webapp/compare/v1.4.51.5...v1.4.52.1)</small>

### Added

- add server init message ([a6bf6bf](https://github.com/dblevin1/docassemble-webapp/commit/a6bf6bfada77a27a24442c74ac4324610956a73d) by Daniel Blevins).

### Fixed

- fix bumpversion config ([36c6e48](https://github.com/dblevin1/docassemble-webapp/commit/36c6e48bb66090aff95ea02dfb79a28c1bc395b8) by Daniel Blevins).
