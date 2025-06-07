// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Mencari dan mengambil kode dari GitHub...'
                checkout scm
            }
        }

        stage('2. Build & Install Dependencies') {
            steps {
                echo 'Mempersiapkan environment dan menginstall dependensi Python...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('3. Unit Test') {
            steps {
                echo 'Menjalankan unit tests dengan Pytest...'
                sh 'pytest tests/'
            }
        }

        stage('4. SAST (Static Analysis with Bandit)') {
            steps {
                echo 'Memindai kode untuk kerentanan dengan Bandit...'
                // -r . : scan semua file di direktori saat ini
                // -ll : hanya laporkan isu dengan level MEDIUM atau HIGH
                // catchError: pipeline tidak akan berhenti jika ada isu, hanya menandainya sebagai unstable
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh 'bandit -r . -ll'
                }
            }
        }

        stage('5. DAST (Dynamic Analysis with ZAP)') {
            steps {
                script {
                    echo 'Membangun Docker image untuk aplikasi...'
                    def dockerImage = docker.build("flask-app-staging:${env.BUILD_ID}")

                    // Jalankan aplikasi di dalam container untuk di-scan oleh ZAP
                    dockerImage.withRun("--name dast-target-app") { c ->
                        echo "Aplikasi sementara berjalan di container ${c.id}"
                        // Tunggu beberapa detik agar aplikasi benar-benar siap
                        sleep 10
                        
                        // Jalankan OWASP ZAP Baseline Scan dari container lain
                        echo "Memulai OWASP ZAP Scan..."
                        try {
                            // --network host: agar container ZAP bisa mengakses port di host machine
                            sh "docker run --rm --network host -v \$(pwd):/zap/wrk/:rw owasp/zap2docker-stable zap-baseline.py -t http://127.0.0.1:8080 -J zap-report.json"
                        } catch (e) {
                            // Gagal jika ZAP menemukan kerentanan
                            error "DAST Scan Gagal! Ditemukan kerentanan: ${e.getMessage()}"
                        } finally {
                           // Publikasikan laporan ZAP sebagai artifact
                           archiveArtifacts artifacts: 'zap-report.json'
                        }
                    }
                }
            }
        }


        stage('6. Deploy to Staging') {
            steps {
                script {
                    echo 'Deployment ke Staging Environment...'
                    def dockerImage = docker.build("flask-app-staging:${env.BUILD_ID}")
                    
                    // Hentikan container staging yang lama jika ada
                    sh 'docker stop staging-app || true'
                    sh 'docker rm staging-app || true'
                    
                    // Jalankan container baru sebagai staging environment
                    dockerImage.run("--name staging-app -p 5000:5000")
                    echo 'Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000'
                }
            }
        }
    }
    
    post {
        always {
            // Selalu jalankan cleanup untuk menghemat ruang disk
            echo 'Membersihkan workspace...'
            cleanWs()
        }
    }
}
