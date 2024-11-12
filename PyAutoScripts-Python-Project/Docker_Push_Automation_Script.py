import sys
import subprocess
from loguru import logger


def prune_docker():
    prune_command = "docker system prune --all --force"
    logger.info(f"Running: {prune_command}")
    subprocess.run(prune_command, shell=True, check=True)
    logger.success("Unused Docker data pruned successfully.")


def build_and_push_docker_image(directory_name, repo_name, aws_account_id, region):
    try:
        # Step 1: Clean up Docker resources
        prune_docker()

        # Step 2: Build the Docker image
        build_command = f"docker build {directory_name} -t {repo_name}"
        logger.info(f"Running: {build_command}")
        subprocess.run(build_command, shell=True, check=True)

        # Step 3: Login to AWS ECR
        login_command = (
            f"aws ecr get-login-password --region {region} | "
            f"docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{region}.amazonaws.com"
        )
        logger.info(f"Running: {login_command}")
        subprocess.run(login_command, shell=True, check=True)

        # Step 4: Tag the Docker image
        tag_command = (
            f"docker tag {repo_name} {aws_account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"
        )
        logger.info(f"Running: {tag_command}")
        subprocess.run(tag_command, shell=True, check=True)

        # Step 5: Push the Docker image to ECR
        push_command = (
            f"docker push {aws_account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"
        )
        logger.info(f"Running: {push_command}")
        subprocess.run(push_command, shell=True, check=True)

        logger.success("Docker image successfully built, tagged, and pushed to AWS ECR.")

        # Step 6: Final Docker cleanup
        prune_docker()

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running the command: {e}")


if __name__ == "__main__":
    interactive = sys.stdin.isatty()

    while True:
        if interactive:
            # Prompt for user inputs at runtime
            directory_name = input("Enter the directory name (where Dockerfile is located): ").strip()
            repo_name = input("Enter the Docker repository name: ").strip()
            aws_account_id = input("Enter your AWS Account ID: ").strip()
            region = input("Enter the AWS region: ").strip()
        else:
            logger.error("This script requires interactive inputs when run outside a CI/CD pipeline.")
            sys.exit(1)

        # Call the function to build and push the Docker image
        build_and_push_docker_image(directory_name, repo_name, aws_account_id, region)

        if not interactive:
            logger.info("Non-interactive execution detected. Exiting after one execution.")
            break

        # Ask the user if they want to run another image
        run_again = input("Do you want to run another image? (Y/n): ").strip()
        if run_again != 'Y':
            logger.info("Exiting the program.")
            break
