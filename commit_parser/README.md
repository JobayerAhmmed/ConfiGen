### Install Requirements

- Python >= 3.8
- Install Jupyter extension in Visual Studio Code to run `IPython` files
    - [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
- Install required packages
    - Open a terminal and go to `configen_workspace` directory that was created in the previous step
    - `source .venv/bin/activate`
    <!-- plotly - generate figures -->
    <!-- kaleido - convert figures to static images -->
    <!-- openpyxl - default engine in pandas -->
    - `pip install pandas openpyxl XlsxWriter requests plotly==5.15.0 kaleido`
    - `pip install jupyter GitPython lxml progressbar2`
    - Build DaisyDiff
        - Install Java (version 1.6 or higher)
            - `sudo apt update`
            - `sudo apt -y install default-jdk`
            - Check installation is success: `java --version`
        - Install Maven
            - `curl -O https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz`
            - `tar -xzvf apache-maven-3.9.6-bin.tar.gz`
            - `sudo mv apache-maven-3.9.6 /opt`
            - Update PATH variable **(follow approach a or b, b is preferred)**
                1) Update PATH temporarily for the current terminal session
                    - `export PATH=$PATH:/opt/apache-maven-3.9.6/bin/`
                2) Update PATH permanently
                    - Open file .bashrc
                        - `nano ~/.bashrc`
                    - Write the following line to the end of this file
                        - `export PATH=$PATH:/opt/apache-maven-3.9.6/bin/`
                    - Save and exit by pressing keys `Ctrl+O` then `Enter` and then `Ctrl+X`
                    - Reload PATH variable
                        - `source ~/.bashrc`
        - Build DaisyDiff JAR
            - `git clone https://github.com/JobayerAhmmed/DaisyDiff.git`
            - `mvn clean package -f DaisyDiff/pom.xml`
            - Error: PKIX path building failed for `org.cyberneko:html`
                - Open `https://maven.nuxeo.org/nexus/content/groups/public/` in Google Chrome
                - Click on site icon left to address in address bar
                - Connection is secure -> Certificate is valid -> Details -> Export
                - Save certificate
                    - Filename: `nuxeo.org.cer`
                    - Format: `DER-encoded binary, single certificate`
                - `keytool -import -alias nuxeo.org -keystore "/usr/lib/jvm/default-java/lib/security/cacerts" -file nuxeo.org.cer`
                    - Change path `*/lib/security/cacerts` according to your system
                    - Change path `nuxeo.org.cer` according to the path where you downloaded the certificate file
                    - Prompt: `yes`
                    - Password: `changeit`
                    - Restart your JVM/PC
    - Build Doxygen (not ConfiGen)
        - `git clone -b Release_1_9_5 --single-branch https://github.com/doxygen/doxygen.git`
        - `cd doxygen`
        - `mkdir build && cd build`
        - `cmake -G "Unix Makefiles" ..`
        - `sudo make`
        - `cd ../..`
