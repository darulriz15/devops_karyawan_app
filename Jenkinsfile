// Jenkinsfile FINAL (dengan perbaikan docker: not found)
pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            // Menjalankan sebagai root agar bisa install paket & menjalankan docker
            args '-v /var/run/docker.sock:/var/run/docker.sock --user root'
        }
    }
    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Mengambil kode dari GitHub...'
                checkout scm
            }
        }
        // TAHAP BARU UNTUK MENGINSTALL DOCKER CLIENT
        stage('2. Setup Environment') {
            steps {
                echo 'Installing Docker client inside the agent...'
                sh 'apt-get update && apt-get install -y docker.io'
            }
        }
        stage('3. Build & Install Dependencies') {
            steps {
                echo 'Menginstall dependensi Python...'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('4. Unit Test') {
            steps {
                echo 'Menjalankan unit tests dengan Pytest...'
                sh 'PYTHONPATH=. pytest tests/'
            }
        }
        stage('5. SAST (Static Analysis with Bandit)') {
            steps {
                echo 'Memindai kode dengan Bandit...'
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh 'bandit -r . -ll'
                }
            }
        }
        stage('6. Build Docker Image') {
            steps {
                echo 'Membangun Docker image untuk aplikasi...'
                sh "docker build -t flask-app-staging:${env.BUILD_ID} ."
            }
        }
	// Jenkinsfile - Ganti Stage 7 dengan ini
	stage('7. DAST (Dynamic Analysis with ZAP)') {
	    steps {
	        script {
	            echo 'Menjalankan container aplikasi untuk DAST...'
	            // Jalankan container aplikasi di background
	            sh "docker run -d --rm --name dast-target-app -p 8088:5000 flask-app-staging:${env.BUILD_ID}"

	            echo 'Menunggu 15 detik agar aplikasi siap...'
	            sleep 15

	            def zapReport = ''
	            try {
	                echo "Memulai OWASP ZAP Scan pada http://127.0.0.1:8088..."
	                // Jalankan ZAP dan simpan output JSON ke variabel 'zapReport'
	                // Opsi -J diganti dengan -T untuk memaksimalkan waktu scan
	                // Kita tidak lagi mount volume -v
	                zapReport = sh(
	                    script: "docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://127.0.0.1:8088 -T 5 -j",
	                    returnStdout: true
	                ).trim()

	            } catch (e) {
	                echo "DAST scan menemukan isu atau gagal dijalankan. Output:"
	                echo e.getMessage()
	                // Tetap simpan laporan jika ada, agar bisa dianalisis
	                zapReport = e.getMessage()
	            } finally {
	                echo 'Menghentikan container aplikasi DAST...'
	                sh 'docker stop dast-target-app || true'

	                if (zapReport) {
	                    echo "Menyimpan laporan DAST ke zap-report.json..."
	                    // Tulis isi variabel ke file
	                    writeFile file: 'zap-report.json', text: zapReport
	                    // Arsipkan file
	                    archiveArtifacts artifacts: 'zap-report.json'
	                } else {
	                    echo "Tidak ada laporan DAST yang dihasilkan."
	                }
	            }
	        }
	    }
	}
        stage('8. Deploy to Staging') {
            steps {
                echo 'Deployment ke Staging Environment...'
                sh 'docker stop staging-app || true'
                sh 'docker rm staging-app || true'
                sh "docker run -d --rm --name staging-app -p 5000:5000 flask-app-staging:${env.BUILD_ID}"
                echo "Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000"
            }
        }
    }
    post {
        always {
            echo 'Membersihkan workspace...'
            cleanWs()
        }
    }
}
