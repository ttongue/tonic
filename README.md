# Tonic extensions to the Seltzer CRM

Seltzer CRM provides a foundation for managing a makerspace membership database. However, there
are a number of business-model specific features that require custom extensions to Seltzer. Tonic is the bundle of extensions written to implement business processes for the Tech Valley Center of Gravity,
including card system access, automated membership provisioning, billing through Braintree and other features.


INSTALLATION
------------
This package requires a custom version of Seltzer and a custom deployment environment. To simplify development and provisioning, use

	https://github.com/ttongue/seltzer-tonic-vagrant

to set up a complete  environment for development. The vagrant-based installation will load tonic and seltzer as submodules and will insure that all of the peices will stay in sync during the development process.